from rest_framework import generics, exceptions
from pico_framework import sers
from pico_framework import models
from pico_framework import consts


class StatsPriceView(generics.ListAPIView):
    pagination_class = None
    serializer_class = sers.StatsMarketPriceSerializer

    def get_queryset(self):
        stock_id = self.request.query_params.get('stock_id')
        unit_id = self.request.query_params.get('unit_id')
        last = self.request.query_params.get('range')

        queryset = models.StatsMarketPrice.objects.all()

        if stock_id and unit_id:
            queryset =queryset.filter(unit_id=unit_id, stock_id=stock_id)

        if last:
            queryset = queryset.filter(
                granularity=consts.GRANULARITY_INVERT_MAP[last])

        else:
            queryset = queryset.filter(
                granularity=consts.GRANULARITY_INVERT_MAP['1h'])

        return queryset
