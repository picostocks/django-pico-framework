import time
from django.test import TestCase

from pico_framework import models
from pico_framework import consts
from pico_framework import tasks

TEST_VALUE = 0


def test_callback(result):
    assert result


class TestCurrencyPrice(TestCase):
    def setUp(self):
        pass

    def test_get_market_price(self):
         price = tasks.get_market_price(3, 2)

         self.assertTrue(price)
         self.assertIsInstance(price, float)

    def test_sync_current_price(self):
        tasks._sync_current_price()
        price = tasks.get_market_price(3, 2)
        instance = models.StatsMarketPrice.objects.first()

        self.assertEqual(price, float(instance.price))

    def test_perform_stats_updates(self):
        self.count = 2
        for _ in range(self.count):
            tasks._sync_current_price()
            tasks._sync_stats_task()
            time.sleep(60)

        stats_minutes = models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_MINUTE)

        self.assertEqual(len(stats_minutes), self.count)

        stats_hour = models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_HOUR)

        self.assertEqual(len(stats_hour), 1, stats_hour)

        stats_week = models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_WEEK)

        self.assertEqual(len(stats_week), 1)

        stats_2week = models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_FORTNIGHTLY)

        self.assertEqual(len(stats_2week), 1)

        stats_month = models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_MONTH)

        self.assertEqual(len(stats_month), 1)

        stats_year = models.StatsMarketPrice.objects.filter(
            granularity=consts.GRANULARITY_YEAR)

        self.assertEqual(len(stats_year), 1)
