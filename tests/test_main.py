from django.test import TestCase

from pico_framework.models import CurrentMarketPrice
from pico_framework.tasks import Sync
from pico_framework.consts import BTC_ID, ETH_ID, STOCK_CHOICES
from pico_framework.settings import tasks_settings


class TestCurrencyPrice(TestCase):
    def setUp(self):
        self.sync = Sync()

    def test_representations_model_currency_pair(self):
        CurrentMarketPrice.objects.create(
            unit_id=BTC_ID, stock_id=ETH_ID, price=23, change=1)
        currency = CurrentMarketPrice.objects.last()
        self.assertEqual(str(currency), '{}\{} - {}'.format(
            STOCK_CHOICES[0][1], STOCK_CHOICES[1][1], currency.price))

    def test_plural_model_currency_pair(self):
        self.assertEqual(CurrentMarketPrice._meta.verbose_name_plural,
                         'current market prices')

    def test_get_market_price(self):
        result = self.sync.get_market_price(BTC_ID, ETH_ID)

        self.assertIn('bids', result)
        self.assertIn('asks', result)

    def test_process(self):
        with self.settings(PICO_FRAMEWORK = {'PAIRS' : [('ETH', 'BTC')]}):
            self.sync.process()

            currencies = CurrentMarketPrice.objects.all()

            self.assertEqual(len(currencies), 1)
