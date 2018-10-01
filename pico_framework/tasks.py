import time
import os
import requests
import importlib
from celery.task import periodic_task
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from pico_framework import models
from pico_framework import settings
from pico_framework import consts
from pico_framework import utils


ORDERBOOK_URL = 'https://api.picostocks.com/v1/market/orderbook/'


def get_market_price(stock_id, unit_id):
    response = requests.get(ORDERBOOK_URL,
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

    aligned_timestamp = utils.align_timestamp(
        granularity=consts.GRANULARITY_MINUTE)
    aligned_datetime = datetime.fromtimestamp(aligned_timestamp)

    for stock_id, unit_id in settings.get_settings('PAIRS'):
        last_stat = models.StatsMarketPrice.objects.filter(
            stock_id=stock_id,
            unit_id=unit_id,
            added=aligned_datetime).first()

        if last_stat:
            continue

        price = get_market_price(stock_id, unit_id)
        if price is None:
            return

        last_stat = models.StatsMarketPrice.objects.create(
            unit_id=unit_id,
            stock_id=stock_id,
            granularity=consts.GRANULARITY_MINUTE,
            price=price,
            added=aligned_datetime
        )

        new_stats.append(last_stat)

    notify_new_price(new_stats)


@periodic_task(run_every=settings.get_settings('SYNC_PRICE_EVERY'))
def sync_current_price_task():
    _sync_current_price()


def _perform_stats_updates(queryset, granularity_kind):
    print('Starts creating stats for granularity {}'.format(granularity_kind))
    # Time in second for each stats
    span_delta = 60 * consts.GRANULARITY_KINDS[granularity_kind]['span']

    # Round to granularity_time
    now_seconds = time.time()
    aligned_timestamp = now_seconds - (now_seconds % span_delta)

    stat_period = datetime.fromtimestamp(aligned_timestamp) - \
                  timedelta(seconds=span_delta)

    stat_queryset = queryset.all().filter(added__gte=stat_period)

    prices = {}

    for item in stat_queryset:

        idx = (item.stock_id, item.unit_id)

        if idx not in prices:
            prices[idx] = {'sum': 0, 'items': 0}

        prices[idx]['sum'] += item.price
        prices[idx]['items'] += 1

    for market, buckets in prices.items():
        sync = aligned_timestamp - span_delta/2

        sync = timezone.datetime.fromtimestamp(sync)

        print('Sync time: {}'.format(sync))

        stat_params = dict(stock_id=market[0], unit_id=market[1],
            granularity=granularity_kind, added=sync)

        with transaction.atomic():
            try:
                stat = models.StatsMarketPrice.objects.get(**stat_params)
                print('Updated price stats for {}'.format(stat_params))
            except models.StatsMarketPrice.DoesNotExist:
                stat = models.StatsMarketPrice(**stat_params)
                print('Created price stats for {}'.format(stat_params))
            stat.price = buckets['sum'] / buckets['items']
            stat.save()

    # Delete stats which are not used more
    if granularity_kind != consts.GRANULARITY_YEAR:
        queryset.filter(added__lt=stat_period).delete()


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


@periodic_task(run_every=settings.get_settings('SYNC_STATS_EVERY'))
def sync_stats_task():
    return _sync_stats_task()
