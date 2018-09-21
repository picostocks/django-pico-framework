from django.test import TestCase

from pico_framework.models import CurrentMarketPrice
from pico_framework.tasks import Sync
from pico_framework.consts import BTC_ID, ETH_ID, STOCK_CHOICES
from pico_framework.utils import get_stats_price


class TestCurrencyPrice(TestCase):
    def setUp(self):
        self.sync = Sync()

    def test_representations_model_currency_pair(self):
        CurrentMarketPrice.objects.create(
            unit_id=BTC_ID, stock_id=ETH_ID, price=23, change=1)
        currency = CurrentMarketPrice.objects.last()
        self.assertEqual(str(currency), '{}\{} - {}'.format(
            STOCK_CHOICES[1][1], STOCK_CHOICES[0][1], currency.price))

    def test_plural_model_currency_pair(self):
        self.assertEqual(CurrentMarketPrice._meta.verbose_name_plural,
                         'current market prices')

    def test_get_stats_price(self):
        CurrentMarketPrice.objects.create(
            unit_id=BTC_ID, stock_id=ETH_ID, price=23, change=1)
        CurrentMarketPrice.objects.create(
            unit_id=BTC_ID, stock_id=ETH_ID, price=21, change=3)
        prices = get_stats_price([(ETH_ID, BTC_ID)])

        self.assertEqual(len(prices), 1)
        self.assertEqual(len(prices[0]), 2)
        self.assertTrue(prices[0][0].get('price'))
