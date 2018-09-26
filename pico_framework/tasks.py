import requests
import importlib

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

            last_stat = models.CurrentMarketPrice.objects.filter(
                stock_id=stock_id, unit_id=unit_id).last()

            last_price = float(last_stat.price) if last_stat else 0

            current_stat = models.CurrentMarketPrice(
                stock_id=stock_id,
                unit_id=unit_id
            )

            current_stat.change = 0

            if last_price:
                current_stat.change = 100*(price - last_price)/min(
                    price, last_price)

            current_stat.price = price
            current_stat.save()
            new_stats.append(last_stat)

        self.call_handlers(new_stats)

    def run_updates_stats(self):
        # Clear old stats from DB
        models.StatsMarketPrice.objects.all().delete()
        for granularity in settings.get_settings('GRANULARITY'):
            queryset = models.CurrentMarketPrice.objects.all()
            utils.perform_updates(queryset,
                                  consts.GRANULARITY_INVERT_MAP[granularity])

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
    return sync.run_updates_stats()
