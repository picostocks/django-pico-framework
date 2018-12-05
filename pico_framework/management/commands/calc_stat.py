from django.core.management.base import BaseCommand
from pico_framework import tasks


class Command(BaseCommand):
    help = 'Run sync_current_price_task.'

    def handle(self, *args, **options):
        tasks._sync_stats_task()
