from django.db import models

from pico_framework import consts


class StatsMarketPrice(models.Model):
    unit_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    stock_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    price = models.DecimalField(max_digits=27, decimal_places=18)
    granularity = models.IntegerField(choices=consts.GRANULARITY_CHOICES)
    added = models.DateTimeField()

    class Meta:
        ordering = ('-added', )
        indexes = [
            models.Index(fields=['unit_id', 'stock_id', 'granularity']),
        ]

    def __str__(self):
        return '{}-{}: {}\{} - {}'.format(self.get_granularity_display(),
                                          self.added,
                                          self.get_stock_id_display(),
                                          self.get_unit_id_display(),
                                          self.price)
