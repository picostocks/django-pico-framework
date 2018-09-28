import time
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from pico_framework import sers
from pico_framework import models
from pico_framework import consts
from pico_framework import settings as pico_settings


def get_stats_price(pairs=None):
    """
    :param pairs: list by tuple
    :return: list
    """

    if pairs is None:
        pairs = pico_settings.get_settings('PAIRS')

    result = []
    for pair in pairs:
        queryset = models.CurrentMarketPrice.objects.filter(
            unit_id=pair[1], stock_id=pair[0])
        if queryset:
            result.append(sers.CurrentMarketPriceSerializer(queryset[0]).data)
    return result


def perform_updates(queryset, granularity_kind):
    print('Starts creating stats for granularity %s' % granularity_kind)
    print('Starts creating stats for granularity {}'.format(granularity_kind))
    # Time in second for each stats
    granularity_seconds = \
        60 * consts.GRANULARITY_KINDS[granularity_kind]['time']

    # Round to granularity_time
    now_seconds = time.time()
    aligned_timestamp = now_seconds - (now_seconds % granularity_seconds)

    span_delta = 60 * consts.GRANULARITY_KINDS[granularity_kind]['span']

    stat_period = datetime.fromtimestamp(aligned_timestamp) - \
                  timedelta(seconds=span_delta)

    stat_queryset = queryset.all().filter(updated__gte=stat_period)

    prices = {}
    for item in stat_queryset:

        idx = (item.stock_id, item.unit_id)

        timestamp_delta = now_seconds - int(item.updated.timestamp())
        bin_id = int(timestamp_delta / granularity_seconds)

        if idx not in prices:
            prices[idx] = {}

        if bin_id not in prices[idx]:
            prices[idx][bin_id] = {'sum': 0, 'items': 0}

        prices[idx][bin_id]['sum'] += item.price
        prices[idx][bin_id]['items'] += 1
    print('Created prices dict: %s' % prices)

    max_bin_id = int(span_delta / granularity_seconds)

    # To ensure we have prices, when no transaction was made during stat period
    if granularity_kind == consts.GRANULARITY_INVERT_MAP['1h']:
        print('Ensure prices for stocks with no transactions made...')
        for stock_id, unit_id in pico_settings.get_settings('PAIRS'):
            idx = (stock_id, unit_id)

            if idx not in prices:
                prices[idx] = {}

            if max_bin_id not in prices[idx]:
                order = queryset.filter(stock_id=stock_id,
                                        unit_id=unit_id).first()
                if not order:
                    continue
                print(
                    'Using latest transaction data (price: %s, idx: %s)' % (
                        order.price, idx
                    ))
                prices[idx] = {max_bin_id: {'sum': order.price, 'items': 1}}
                print('Price stats for stocks with no transactions were filled.')

            for bin_id in range(max(prices[idx])-1, -1, -1):
                print('Filling up gaps.. using price from previous bins.')
                if bin_id not in prices[idx]:
                    print('Adding new bin id: %s for idx: %s' % (bin_id, idx))
                    prices[idx][bin_id] = prices[idx][bin_id+1]
                print('Finished filling up gaps.')

    for market, buckets in prices.items():
        for bin_id, market_stat in buckets.items():
            sync = now_seconds - bin_id * granularity_seconds - int(
                granularity_seconds/2)
            sync = timezone.datetime.fromtimestamp(sync, tz=timezone.utc)

            stat_params = dict(
                stock_id=market[0],
                unit_id=market[1],
                granularity=granularity_kind,
                updated=sync
            )

            with transaction.atomic():
                try:
                    stat = models.StatsMarketPrice.objects.get(**stat_params)
                    print('Created price stats for %s' % stat_params)
                except models.StatsMarketPrice.DoesNotExist:
                    stat = models.StatsMarketPrice(**stat_params)
                stat.price = market_stat['sum'] / market_stat['items']
                stat.save()

    # Delete stats which are not used more
    if granularity_kind not in [consts.GRANULARITY_INVERT_MAP['1h'],
                                consts.GRANULARITY_INVERT_MAP['year']]:
        queryset.filter(updated__lt=stat_period).delete()

    if granularity_kind == consts.GRANULARITY_INVERT_MAP['1h']:
        queryset.filter(
            updated__lt=timezone.now() - timedelta(days=1)).delete()
