from datetime import timedelta
from django.utils import timezone
from django.db import models

from pico_framework import consts


class CurrentMarketPrice(models.Model):
    unit_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    stock_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    price = models.DecimalField(max_digits=18, decimal_places=9)
    change = models.FloatField()
    updated = models.DateTimeField(auto_now_add=True)
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


class StatsMarketPrice(models.Model):
    unit_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    stock_id = models.IntegerField(choices=consts.STOCK_CHOICES)
    price = models.DecimalField(max_digits=18, decimal_places=9)
    granularity = models.IntegerField(choices=consts.GRANULARITY_CHOICES)
    updated = models.DateTimeField()
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id', )
        indexes = [
            models.Index(fields=['unit_id', 'stock_id', 'granularity']),
        ]

    def __str__(self):
        return '{}: {}\{} - {}'.format(self.get_granularity_display(),
                                       self.get_stock_id_display(),
                                       self.get_unit_id_display(),
                                       self.price)

    @classmethod
    def last_day_stats(cls, **kwargs):
        granularity = consts.GRANULARITY_INVERT_MAP['7d']
        yesterday = timezone.localtime(timezone.now()) - timedelta(days=1)
        return cls.objects.filter(granularity=granularity,
                                  updated__year=yesterday.year,
                                  updated__month=yesterday.month,
                                  updated__day=yesterday.day, **kwargs)
