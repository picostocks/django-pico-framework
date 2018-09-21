from django.db import models

from pico_framework import consts


class CurrentMarketPrice(models.Model):
    unit_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    stock_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    price = models.DecimalField(max_digits=18, decimal_places=9)
    change = models.FloatField()
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)
        indexes = [
            models.Index(fields=['unit_id', 'stock_id']),
        ]

    def __str__(self):
        return '{}\{} - {}'.format(self.get_stock_id_display(),
                                   self.get_unit_id_display(),
                                   self.price)
