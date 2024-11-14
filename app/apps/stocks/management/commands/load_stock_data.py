from django.core.management.base import BaseCommand, CommandParser

from ...tasks import load_stock_data


class Command(BaseCommand):
    help = 'Загружает данные о акциях в базу данных из внешнего API.'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '-U', '--update',
            action='store_true',
            help='Обновить исторические данные для последнего доступного периода.',
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        update = options.get('update', False)

        self.stdout.write(f'Загрузка {"последних" if update else "всех"} данных об акциях...'
                          f' (подробности в app/logs/celery.log)')

        load_stock_data.delay(update=update)
