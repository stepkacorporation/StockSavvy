from django.core.management.base import BaseCommand

from ...tasks import load_available_stocks


class Command(BaseCommand):
    help = 'Loads stock data into the database from an external API.'

    def handle(self, *args, **options):
        load_available_stocks.delay()
