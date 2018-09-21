from pico_framework import sers
from pico_framework import models


def get_stats_price(pairs: list):
    """
    :param pairs: list by tuple
    :return: list
    """
    result = []
    for pair in pairs:
        try:
            qeuryset = models.CurrentMarketPrice.objects.filter(
                unit_id=pair[1], stock_id=pair[0])
        except models.CurrentMarketPrice.DoesNotExist:
            pass
        else:
            result.append(sers.CurrentMarketPriceSerializer(
                qeuryset, many=True).data)

    return result
