from pico_framework import sers
from pico_framework import models


def get_stats_price(pairs: list):
    result = []
    for pair in pairs:
        try:
            obj = models.CurrentMarketPrice.objects.get(unit_id=pair[1],
                                                        stock_id=pair[0])
        except models.CurrentMarketPrice.DoesNotExist:
            pass
        else:
            result.append(obj)

    return sers.CurrentMarketPriceSerializer(result, many=True).data
