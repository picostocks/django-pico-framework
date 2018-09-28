import time, datetime
from django.db.models import Avg

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
            unit_id=pair[1], stock_id=pair[0], granurality=consts.GRANULARITY_MINUTE)
        if queryset:
            result.append(sers.CurrentMarketPriceSerializer(queryset.last()).data)
    return result


def get_price_stats(stock_id, unit_id, granturality=consts.GRANULARITY_FORTNIGHTLY):
    queryset = models.StatsMarketPrice.objects.filter(granturality=granturality)

    if stock_id and unit_id:
        queryset = queryset.filter(unit_id=unit_id, stock_id=stock_id)

    return sers.StatsMarketPriceSerializer(queryset, many=True).data


def align_timestamp(timestamp_seconds=None, granurality=consts.GRANULARITY_HOUR):
    if timestamp_seconds is None:
        timestamp_seconds = time.time()

    granularity_seconds = 60 * consts.GRANULARITY_KINDS[granurality]['time']
    return timestamp_seconds - (timestamp_seconds % granularity_seconds)


def get_change(stock_id, unit_id):
    day_seconds = 24*60*60

    yestarday_timestamp_seconds = time.time() - day_seconds
    yestarday_timestamp_aligned = int(yestarday_timestamp_seconds/day_seconds)*day_seconds
    yestarday_aligned = datetime.fromtimestamp(yestarday_timestamp_aligned)

    return models.StatsMarketPrice.objects.objects.filter(
        granularity=consts.GRANULARITY_FORTNIGHTLY,
        added = yestarday_aligned,
        stock_id = stock_id,
        unit_id=unit_id
    ).aggregate(Avg('price'))['price__avg']
