from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает суперпользователя с предустановленными данными'

    def handle(self, *args, **kwargs):
        self.stdout.write(f'Создание суперпользователя по умолчанию...')

        username = 'admin'
        email = 'admin@admin.com'
        password = 'admin'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь "{username}" создан'))
        else:
            self.stdout.write(self.style.WARNING(f'Суперпользователь "{username}" уже существует'))
