import datetime
import random
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from pico_framework import models
from pico_framework.tasks import Sync
from pico_framework.consts import BTC_ID, ETH_ID, STOCK_CHOICES
from pico_framework.utils import get_stats_price


class TestCurrencyPrice(TestCase):
    def setUp(self):
        self.sync = Sync()

    def _create_price_markets(self, r, count):
        last = None
        for _ in range(count):
            time_ = timezone.localtime(timezone.now()) - datetime.timedelta(
                minutes=random.randint(1, r))

            price = random.randint(1, 100)

            last = models.CurrentMarketPrice.objects.create(
                unit_id=BTC_ID, stock_id=ETH_ID,
                price=price, change=abs(last.price - price)
                if last else 0)
            last.updated = time_
            last.save()
        Sync().run_updates_stats()

    def test_representations_model_currency_pair(self):
        models.CurrentMarketPrice.objects.create(
            unit_id=BTC_ID, stock_id=ETH_ID, price=23, change=1)
        currency = models.CurrentMarketPrice.objects.last()
        self.assertEqual(str(currency), '{}\{} - {}'.format(
            STOCK_CHOICES[1][1], STOCK_CHOICES[0][1], currency.price))

    def test_plural_model_currency_pair(self):
        self.assertEqual(models.CurrentMarketPrice._meta.verbose_name_plural,
                         'current market prices')

    def test_get_price(self):
        models.CurrentMarketPrice.objects.create(
            unit_id=BTC_ID, stock_id=ETH_ID, price=23, change=1)
        models.CurrentMarketPrice.objects.create(
            unit_id=BTC_ID, stock_id=ETH_ID, price=21, change=3)
        prices = get_stats_price([(ETH_ID, BTC_ID)])

        self.assertEqual(len(prices), 1)
        self.assertTrue(len(prices[0]))
        self.assertTrue(prices[0].get('price'))

    def test_get_stats(self):
        self._create_price_markets(r=500000, count=1000)
        self.assertTrue(len(models.StatsMarketPrice.objects.filter(
            granularity=6)))

        url = reverse('pico-framework-stats')

        self.assertTrue('pico-framework' in url)

        response = self.client.get(url, {'range': 'year'})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertTrue(response.json())

    def test_get_stats_with_not_correct_pair(self):
        self._create_price_markets(r=500000, count=1000)
        self.assertTrue(len(models.StatsMarketPrice.objects.filter(
            granularity=6)))

        url = reverse('pico-framework-stats')

        self.assertTrue('pico-framework' in url)

        response = self.client.get(url, {'range': 'year', 'stock_id': 4,
                                         'unit_id': 5})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertFalse(response.json())

    def test_get_stats_with_correct_pair(self):
        self._create_price_markets(r=500000, count=1000)
        self.assertTrue(len(models.StatsMarketPrice.objects.filter(
            granularity=6)))

        url = reverse('pico-framework-stats')

        self.assertTrue('pico-framework' in url)

        response = self.client.get(url, {'range': 'year', 'stock_id': 3,
                                         'unit_id': 2})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertTrue(response.json())
