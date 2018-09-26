import time
from datetime import datetime, timedelta
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db.models import Avg, Count

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

    start_date = stat_period
    finish_date = stat_period + timedelta(seconds=granularity_seconds)
    names_stocks = stat_queryset.order_by('stock_id', 'unit_id').distinct(
        'stock_id', 'unit_id').values('stock_id', 'unit_id')

    prices = {}
    for item in names_stocks:

        bind_id = 0

        while True:

            idx = (item['stock_id'], item['unit_id'])
            # All current pair in this time slice
            stat = stat_queryset.filter(
                updated__gte=start_date, updated__lt=finish_date,
                stock_id=item['stock_id'], unit_id=item['unit_id']).\
                order_by('-updated')

            # Agregate
            value = stat.annotate(
                average_price=Avg('price')).\
                aggregate(Avg('average_price'), items=Count('id'))

            if value['average_price__avg']:
                bind_id += 1
                if idx not in prices:
                    prices[idx] = {}

                if bind_id not in prices[idx]:
                    prices[idx][bind_id] = {'avg': 0, 'items': 0}

                prices[idx][bind_id]['avg'] = value['average_price__avg']
                prices[idx][bind_id]['items'] = value['items']

            start_date = finish_date
            finish_date = finish_date + timedelta(seconds=granularity_seconds)

            if start_date > datetime.fromtimestamp(aligned_timestamp):
                break

    print('Created prices dict: %s' % prices)

    for market, buckets in prices.items():
        for bin_id, market_stat in buckets.items():
            updated = now_seconds - int(granularity_seconds / 2)

            updated = timezone.datetime.fromtimestamp(updated)

            stat_params = dict(
                stock_id=market[0],
                unit_id=market[1],
                granularity=granularity_kind,
                updated=updated,
                price=market_stat['avg']
            )

            with transaction.atomic():
                try:
                    try:
                        stat = models.StatsMarketPrice.objects.get(**stat_params)
                    except models.StatsMarketPrice.DoesNotExist:
                        stat = models.StatsMarketPrice(**stat_params)
                    stat.save()
                    print('Created price stats for %s' % stat_params)
                except IntegrityError:
                    pass
