from pico_framework import sers
from pico_framework import models

from django.conf import settings


def get_stats_price(pairs=None):
    """
    :param pairs: list by tuple
    :return: list
    """

    if pairs is None:
        pairs = settings.PICO_FRAMEWORK.get('PAIRS', [])

    result = []
    for pair in pairs:
        qeuryset = models.CurrentMarketPrice.objects.filter(
            unit_id=pair[1], stock_id=pair[0])
        if qeuryset:
            result.append(sers.CurrentMarketPriceSerializer(
                qeuryset, many=True).data)
    return result
