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

    def _create_price_markets(self, count, r=60, hours=0):
        last = None
        for _ in range(count):
            time_ = timezone.localtime(timezone.now()) - \
                    datetime.timedelta(hours=hours) - \
                    datetime.timedelta(minutes=random.randint(0, r))

            price = random.randint(1, 100)
            last = models.CurrentMarketPrice.objects.create(
                unit_id=BTC_ID, stock_id=ETH_ID,
                price=price, change=abs(last.price - price)
                if last else 0)
            last.updated = time_
            last.save()
        Sync().run_updates()

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
        self._create_price_markets(count=1000)
        self.assertTrue(len(models.StatsMarketPrice.objects.filter(
            granularity=1)))

        url = reverse('pico-framework-stats')

        self.assertTrue('stats' in url)

        response = self.client.get(url, {'range': '1h'})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertTrue(response.json())

    def test_get_stats_with_not_correct_pair(self):
        self._create_price_markets(count=1000)
        self.assertTrue(len(models.StatsMarketPrice.objects.filter(
            granularity=1)))

        url = reverse('pico-framework-stats')

        self.assertTrue('stats' in url)

        response = self.client.get(url, {'range': '1h', 'stock_id': 4,
                                         'unit_id': 5})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertFalse(response.json())

    def test_get_stats_for_day(self):
        for i in range(1, 24):
            self._create_price_markets(count=100, hours=i)
        self.assertTrue(len(models.StatsMarketPrice.objects.filter(
            granularity=2)))

        url = reverse('pico-framework-stats')

        self.assertTrue('stats' in url)

        response = self.client.get(url, {'range': '24h', 'stock_id': 3,
                                         'unit_id': 2})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertTrue(response.json())

    def test_get_stats_for_week(self):
        for i in range(0, 7):
            self._create_price_markets(count=10, hours=24*i)
        self.assertTrue(len(models.StatsMarketPrice.objects.filter(
            granularity=3)))

        url = reverse('pico-framework-stats')

        self.assertTrue('stats' in url)

        response = self.client.get(url, {'range': '7d', 'stock_id': 3,
                                         'unit_id': 2})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertTrue(response.json())
        self.assertEqual(
            len(response.json()),
            len(models.StatsMarketPrice.objects.filter(granularity=3)))
