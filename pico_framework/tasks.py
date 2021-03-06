import importlib
import time

import requests
from celery import shared_task
from django.db import transaction
from pico_framework import consts
from pico_framework import models
from pico_framework import settings
from pico_framework import utils

PICO_ORDERBOOK_URL = 'https://api.picostocks.com/v1/market/orderbook/'
COINPAPRICA_URL = 'https://api.coinpaprika.com/v1/ticker/'


def get_bst_usd_price(ticker_name='bst-blockstamp'):
    url = COINPAPRICA_URL + ticker_name

    try:
        return float(requests.get(url).json()['price_usd'])
    except Exception as e:
        return None


def get_market_price(stock_id, unit_id):
    response = requests.get(PICO_ORDERBOOK_URL,
                            {'unit_id': unit_id, 'stock_id': stock_id})

    if response.status_code != 200:
        return None

    response = response.json()

    bids, asks = response['bids'], response['asks']
    if not bids or not asks:
        return None

    return (float(bids[0]['price']) + float(asks[0]['price'])) / 2


def notify_new_price(price_stats):
    for path in settings.get_settings('CALLBACK_TASK'):
        s_path = path.split('.')
        callback = s_path[-1]
        module_path = '.'.join(s_path[:-1])
        module = importlib.import_module(module_path)

        callback = getattr(module, callback)

        if hasattr(callback, '__call__'):
            callback(price_stats)


def _sync_current_price():
    new_stats = []

    aligned_timestamp = utils.align_timestamp(granularity=consts.GRANULARITY_MINUTE)

    for stock_id, unit_id in settings.get_settings('PAIRS'):
        last_stat = models.StatsMarketPrice.objects.filter(
            stock_id=stock_id,
            unit_id=unit_id,
            granularity=consts.GRANULARITY_MINUTE,
            timestamp=aligned_timestamp).first()

        if last_stat is not None:
            continue

        if stock_id == consts.BST_ID and unit_id == consts.USD_ID:
            price = get_bst_usd_price()
        else:
            price = get_market_price(stock_id, unit_id)

        if price is None:
            return

        last_stat = models.StatsMarketPrice.objects.create(
            unit_id=unit_id,
            stock_id=stock_id,
            granularity=consts.GRANULARITY_MINUTE,
            price=price,
            timestamp=aligned_timestamp
        )

        new_stats.append(last_stat)

    # Remove stats older than 1 hour
    models.StatsMarketPrice.objects.filter(
        granularity=consts.GRANULARITY_MINUTE,
        timestamp__lt=aligned_timestamp - 3600
    ).delete()

    notify_new_price(new_stats)


@shared_task
def sync_current_price_task():
    _sync_current_price()


def _perform_stats_updates(queryset, granularity_kind):
    granularity_time = 60 * consts.GRANULARITY_KINDS[granularity_kind]['time']
    now_seconds = int(time.time())

    # Recalculate data for last 2 timeframes in particular granularity
    stat_period = now_seconds - 2 * granularity_time
    stat_period -= stat_period % granularity_time

    stat_queryset = queryset.all().filter(timestamp__gte=stat_period)

    prices = {}
    for item in stat_queryset:
        idx = (item.stock_id, item.unit_id)
        if idx not in prices:
            prices[idx] = {}

        timestamp_delta = int(item.timestamp - stat_period)
        bin_id = int(timestamp_delta / granularity_time)
        if bin_id not in prices[idx]:
            prices[idx][bin_id] = {'sum': 0, 'items': 0}

        prices[idx][bin_id]['sum'] += item.price
        prices[idx][bin_id]['items'] += 1

    for market, buckets in prices.items():
        for bin_id, market_stat in buckets.items():
            sync = stat_period + bin_id * granularity_time - int(granularity_time / 2)

            stat_params = dict(
                stock_id=market[0],
                unit_id=market[1],
                granularity=granularity_kind,
                timestamp=sync)

            with transaction.atomic():
                try:
                    stat = models.StatsMarketPrice.objects.get(**stat_params)
                except models.StatsMarketPrice.DoesNotExist:
                    stat = models.StatsMarketPrice(**stat_params)
                stat.price = market_stat['sum'] / market_stat['items']
                stat.save()

    # Delete stats which are not used more
    if granularity_kind != consts.GRANULARITY_YEAR:
        span_delta = 60 * consts.GRANULARITY_KINDS[granularity_kind]['span']
        models.StatsMarketPrice.objects.filter(
            timestamp__lt=stat_period - span_delta,
            granularity=granularity_kind
        ).delete()


def _sync_stats_task():
    for queryset, granularity_kind in [
        (models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_MINUTE),
         consts.GRANULARITY_HOUR),

        (models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_HOUR),
         consts.GRANULARITY_DAY),

        (models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_DAY),
         consts.GRANULARITY_WEEK),

        (models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_WEEK),
         consts.GRANULARITY_FORTNIGHTLY),

        (models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_FORTNIGHTLY),
         consts.GRANULARITY_MONTH),

        (models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_MONTH),
         consts.GRANULARITY_YEAR)]:

        _perform_stats_updates(queryset, granularity_kind)


@shared_task
def sync_stats_task():
    return _sync_stats_task()
