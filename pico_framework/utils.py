import time
import datetime
from django.db.models import Avg, Q

from pico_framework import sers
from pico_framework import models
from pico_framework import consts
from pico_framework import settings as pico_settings


def get_current_price(pairs=None):
    """
    :param pairs: list by tuple
    :return: list
    """

    if pairs is None:
        pairs = pico_settings.get_settings('PAIRS')

    result = []
    for pair in pairs:
        queryset = models.StatsMarketPrice.objects.filter(
            unit_id=pair[1], stock_id=pair[0], granularity=consts.GRANULARITY_MINUTE)
        if queryset:
            result.append(sers.CurrentMarketPriceSerializer(queryset.last()).data)
    return result


def get_price_stats(pairs=None, granularity=consts.GRANULARITY_FORTNIGHTLY):

    if pairs is None:
        pairs = pico_settings.get_settings('PAIRS')

    result = []
    for pair in pairs:
        queryset = models.StatsMarketPrice.objects.filter(granularity=granularity,
                                                          stock_id = pair[0],
                                                          unit_id = pair[1])
        if queryset:
            result.append({
                'stock_id':pair[0],
                'unit_id':pair[1],
                'values':sers.StatsMarketPriceSerializer(queryset, many=True).data
            })
    return result


def align_timestamp(timestamp_seconds=None, granularity=consts.GRANULARITY_HOUR):
    if timestamp_seconds is None:
        timestamp_seconds = time.time()

    granularity_seconds = 60 * consts.GRANULARITY_KINDS[granularity]['time']
    return timestamp_seconds - (timestamp_seconds % granularity_seconds)


def get_change(stock_id, unit_id):
    day_seconds = 24 * 60 * 60

    yesterday_timestamp_seconds = int(time.time() - day_seconds)
    yesterday_timestamp_seconds -= yesterday_timestamp_seconds % day_seconds

    return models.StatsMarketPrice.objects.filter(
        Q(granularity=consts.GRANULARITY_WEEK_TIME)&
        Q(stock_id = stock_id)&
        Q(unit_id=unit_id)&
        Q(timestamp__gt=yesterday_timestamp_seconds)&
        Q(timestamp__lte=yesterday_timestamp_seconds+day_seconds)
    ).aggregate(Avg('price'))['price__avg']
