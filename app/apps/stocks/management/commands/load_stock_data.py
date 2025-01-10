from django.core.management.base import BaseCommand, CommandParser
from ...tasks import load_stock_data
from datetime import datetime


class Command(BaseCommand):
    help = 'Загружает данные о акциях в базу данных из внешнего API за указанный период.'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--start_date', '-S',
            type=str,
            help='Начальная дата периода в формате "YYYY-MM-DD".',
        )
        parser.add_argument(
            '--end_date', '-E',
            type=str,
            help='Конечная дата периода в формате "YYYY-MM-DD".',
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        start_date = options.get('start_date')
        end_date = options.get('end_date')

        # Проверка формата даты
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            self.stderr.write('Ошибка: Убедитесь, что даты указаны в формате "YYYY-MM-DD".')
            return

        self.stdout.write(f'Запуск задачи загрузки данных об акциях за период '
                          f'{start_date or "все время"} - {end_date or "текущее время"}...')
        load_stock_data.delay(start_date=start_date, end_date=end_date)
