from django.core.management.base import BaseCommand, CommandError
from pico_framework import tasks

class Command(BaseCommand):
    help = 'Run sync_stats_task.'

    def handle(self, *args, **options):
        tasks._sync_current_price()

