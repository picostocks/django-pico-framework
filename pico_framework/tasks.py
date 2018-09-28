import requests
import importlib
from django.db.models import Avg
from celery.task import periodic_task

from pico_framework import models
from pico_framework import settings
from pico_framework import utils
from pico_framework import consts


class Sync(object):
    api_url = 'https://api.picostocks.com/v1/'
    orderbook_url = api_url + 'market/orderbook/'

    def process(self):
        new_stats = []

        for stock_id, unit_id in settings.get_settings('PAIRS'):
            price = self.get_market_price(stock_id, unit_id)
            if price is None:
                return

            last_stat = models.StatsMarketPrice.last_day_stats(
                stock_id=stock_id, unit_id=unit_id)

            current_stat = models.CurrentMarketPrice(
                stock_id=stock_id, unit_id=unit_id)

            current_stat.change = 0

            if last_stat:
                current_stat.change = \
                    last_stat.aggregate(Avg(price))['price__avg']

            current_stat.price = price
            current_stat.save()
            new_stats.append(last_stat)

        self.call_handlers(new_stats)

    def run_updates(self):
        for queryset, granularity_kind in [
            (models.CurrentMarketPrice.objects.all(),
             consts.GRANULARITY_INVERT_MAP['1h']),

            (models.StatsMarketPrice.objects.filter(
                granularity=consts.GRANULARITY_INVERT_MAP['1h']),
             consts.GRANULARITY_INVERT_MAP['24h']),

            (models.StatsMarketPrice.objects.filter(
                granularity=consts.GRANULARITY_INVERT_MAP['24h']),
             consts.GRANULARITY_INVERT_MAP['7d']),

            (models.StatsMarketPrice.objects.filter(
                granularity=consts.GRANULARITY_INVERT_MAP['7d']),
             consts.GRANULARITY_INVERT_MAP['14d']),

            (models.StatsMarketPrice.objects.filter(
                granularity=consts.GRANULARITY_INVERT_MAP['14d']),
             consts.GRANULARITY_INVERT_MAP['month']),

            (models.StatsMarketPrice.objects.filter(
                granularity=consts.GRANULARITY_INVERT_MAP['month']),
             consts.GRANULARITY_INVERT_MAP['year'])]:

            utils.perform_updates(queryset, granularity_kind)

    def get_market_price(self, stock_id, unit_id):
        response = requests.get(self.orderbook_url,
                                {'unit_id': unit_id, 'stock_id': stock_id})

        if response.status_code != 200:
            return None

        response = response.json()

        bids, asks = response['bids'], response['asks']
        if not bids or not asks:
            return None

        return (float(bids[0]['price']) + float(asks[0]['price']))/2

    def call_handlers(self, price_stats):
        for path in settings.get_settings('CALLBACK_TASK'):
            s_path = path.split('.')
            callback = s_path[-1]
            module_path = '.'.join(s_path[:-1])
            module = importlib.import_module(module_path)

            callback = getattr(module, callback)

            if hasattr(callback, '__call__'):
                callback(price_stats)


@periodic_task(run_every=settings.get_settings('SYNC_TASK_EVERY'))
def sync_task():
    sync = Sync()
    return sync.process()


@periodic_task(run_every=settings.get_settings('SYNC_GRANULARITY_EVERY'))
def sync_task():
    sync = Sync()
    return sync.run_updates()
