import os
import logging

from logging.handlers import RotatingFileHandler

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, task_failure

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('stocks', broker_connection_retry=False, broker_connection_retry_on_startup=True)
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-available-stocks-every-day': {
        'task': 'apps.stocks.tasks.load_available_stocks',
        'schedule': crontab(minute=0, hour=0),
    },
    'load-new-candles-for-all-available-stocks-every-day': {
        'task': 'apps.stocks.tasks.load_latest_historical_data',
        'schedule': crontab(minute=0, hour=0),
    },
}


@task_failure.connect
def handle_task_failure(task_id, exception, args, kwargs, traceback, einfo, **kw):
    """
    The Celery task error handler.
    Sends an error notification to the site administrators.
    """

    UserModel = get_user_model()
    admins = UserModel.objects.filter(is_staff=True)

    subject = 'Error in Celery task'
    message = f'An error occurred in Celery task[{task_id}]: {exception}\n\n{einfo}'

    for admin in admins:
        send_mail(subject, message, None, [admin.email])


@after_setup_logger.connect
def after_setup_celery_logger(logger, **kwargs):
    """Adds a file logger setup function to the Celery logger after setup signal."""

    logger = add_file_logger(logger)
    return logger


def add_file_logger(logger: logging.RootLogger) -> logging.RootLogger:
    """
    Configures logging to a file for the logger.
    It takes values from the LOGGING file variable settings.py.

    Parameters:
        logger (logging.RootLogger): Root logger object to which the file handler will be added.

    Returns:
        logging.RootLogger: The logger object with the file handler configured.
    """

    handler_settings = settings.LOGGING.get('handlers').get('celery')
    formatter_settings = settings.LOGGING.get('formatters').get('verbose')
    logger_settings = settings.LOGGING.get('loggers').get('celery')

    file_handler = RotatingFileHandler(
        filename=handler_settings.get('filename'),
        maxBytes=handler_settings.get('maxBytes'),
        backupCount=handler_settings.get('backupCount'),
    )
    formatter = logging.Formatter(fmt=formatter_settings.get('format'), style=formatter_settings.get('style'))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.setLevel(logger_settings.get('level'))
    logger.propagate = logger_settings.get('propagate')

    return logger
