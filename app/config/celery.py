import logging
import os
import sys

from celery import Celery
# from celery.schedules import crontab
from celery.signals import after_setup_logger, task_failure, after_setup_task_logger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from loguru import logger as loguru_logger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('app', broker_connection_retry=False, broker_connection_retry_on_startup=True)
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


# app.conf.beat_schedule = {
#     'update-stock-data-every-day': {
#         'task': 'apps.stocks.tasks.load_stock_data',
#         'schedule': crontab(minute=0, hour=0),
#         'kwargs': {'update': True},
#     },
# }


@task_failure.connect
def handle_task_failure(task_id, exception, args, kwargs, traceback, einfo, **kw):
    """
    Обрабатывает ошибки в задачах Celery и отправляет уведомление всем администраторам.
    """

    User = get_user_model()

    admins = User.objects.filter(is_staff=True)

    subject = 'Ошибка в задаче Celery'
    message = f'Произошла ошибка в задаче Celery\n\nID={task_id}\n\n{exception}\n\n{einfo}'

    for admin in admins:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin.email])


def setup_loguru_logger():
    """Настраиваем loguru для Celery и перенаправляем стандартные логи"""
    # Очищаем обработчики loguru
    loguru_logger.remove()

    # Устанавливаем уровень логирования
    level = 'DEBUG' if settings.DEBUG else 'INFO'

    # Определяем формат в стиле Celery
    celery_format = "[{time:YYYY-MM-DD HH:mm:ss,SSS}: {level}/{process.name}] {message}"

    # Добавляем обработчики loguru
    loguru_logger.add(sys.stdout, level=level, format=celery_format, enqueue=True)
    loguru_logger.add('app/logs/celery.log', level=level, rotation='10 MB', retention='7 days', compression='zip',
                      format=celery_format)

    # Создаем адаптер для перенаправления стандартных логов в loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Получаем соответствующий уровень loguru
            level_ = loguru_logger.level(record.levelname).name if loguru_logger.level(
                record.levelname) else record.levelno
            # Отправляем сообщение в loguru
            loguru_logger.log(level_, record.getMessage())

    # Подключаем обработчик к корневому логгеру
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level)


@after_setup_logger.connect
def setup_celery_logger(logger, **kwargs):
    """Перенастраиваем корневой логер Celery на использование loguru"""

    setup_loguru_logger()


@after_setup_task_logger.connect
def setup_celery_task_logger(logger, **kwargs):
    """Настраиваем логирование loguru для задач Celery"""

    setup_loguru_logger()
