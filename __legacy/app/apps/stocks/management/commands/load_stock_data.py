from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings

from ...tasks import load_stock_data


class Command(BaseCommand):
    help = 'Loads stock data into the database from an external API.'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '-U', '--update',
            action='store_true',
            help='Update historical data for the latest available period.',
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        update = options.get('update', False)

        try:
            logging_dir = settings.LOGGING['handlers']['celery']['filename']
        except Exception:
            self.stdout.write(self.style.ERROR('The path to the celery logging file was'
                                               ' not found. The task cannot be started.'))
            return None

        self.stdout.write(f'Loading {"latest" if update else "all"} stock data... (details in {logging_dir})')

        load_stock_data.delay(update=update)
