import requests
import importlib

from celery.task import periodic_task

from pico_framework.models import CurrentMarketPrice
from pico_framework.settings import tasks_settings


class Sync(object):
    api_url = 'https://api.picostocks.com/v1/'
    orderbook_url = api_url + 'market/orderbook/'

    def process(self):
        new_stats = []

        for stock_id, unit_id in tasks_settings.PAIRS:
            price = self.get_market_price(stock_id, unit_id)
            if price is None:
                return

            try:
                last_stat = CurrentMarketPrice.objects.get(
                    stock_id=stock_id,
                    unit_id=unit_id)
            except CurrentMarketPrice.DoesNotExist:
                last_stat = CurrentMarketPrice(
                    stock_id=stock_id,
                    unit_id=unit_id
                )

            last_stat.change = 0
            if last_stat.price:
                last_stat.change = 100*(price - last_stat.price)/price

            last_stat.price = price
            last_stat.save()
            new_stats.append(last_stat)

        self.call_handlers(new_stats)

    def get_market_price(self, stock_id, unit_id):
        response = requests.get(self.orderbook_url,
                                {'unit_id': unit_id, 'stock_id': stock_id})

        if response.status_code != 200:
            return None

        response = response.json()

        bids, asks = response['bids'], response['asks']
        if not bids or not asks:
            return None

        return (bids[0]['price'] + asks[0]['price'])/2

    def call_handlers(self, price_stats):
        for path in tasks_settings.CALLBACK_TASK:
            s_path = path.split('.')
            callback = s_path[-1]
            module_path = '.'.join(s_path[:-1])
            module = importlib.import_module(module_path)

            callback = getattr(module, callback)

            if hasattr(callback, '__all__'):
                callback(price_stats)


@periodic_task(run_every=tasks_settings.SYNC_TASK_EVERY)
def sync_task():
    sync = Sync()
    return sync.process()
