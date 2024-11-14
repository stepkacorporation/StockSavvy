from datetime import date, timedelta
from time import perf_counter

import celery
from celery.exceptions import Retry
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.backends.postgresql.psycopg_any import DateTimeRange
from loguru import logger
from moexalgo import Market
from requests.exceptions import RequestException

from app.config.celery import app
from .models import Stock, Candle, PriceChange
from .utils.tasks import (
    get_available_dates,
    load_candles,
    calculate_price_change_per_day,
    calculate_price_change_per_year
)


@app.task
def _log_execution_time(start_time: float, message: str) -> float:
    """
    Логирует время выполнения задачи.

    Параметры:
        - start_time (float): Время начала выполнения задачи.
        - message (str): Сообщение, которое будет залогировано вместе с временем выполнения.

    Возвращает:
        - float: Время выполнения задачи в секундах.
    """

    execution_time = perf_counter() - start_time
    logger.info(f'{message} {execution_time}с')
    return execution_time


@app.task
def load_stock_data(update: bool = False) -> None:
    """
    Запускает задачи для загрузки доступных акций, исторических данных
    и изменений цен для всех загруженных доступных акций.

    Параметры:
        - update (bool): Если True, загружает исторические данные за последний доступный период.
        Если False, загружает исторические данные за все доступные периоды.

    Возвращает:
        - None
    """

    logger.info('Начало загрузки данных об акциях')
    _start_time = perf_counter()
    _execution_message = 'Данные о акциях успешно загружены за'

    load_historical_data_func = load_latest_historical_data if update else load_historical_data

    celery.chain(
        load_available_stocks.si(),
        load_historical_data_func(),
        load_price_changes(),
        _log_execution_time.si(_start_time, _execution_message),
    ).apply_async()


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 10})
def load_available_stocks() -> int:
    """
    Загружает доступные акции с рынка и создает или обновляет объекты Stock в базе данных.

    Возвращает:
        - int: Количество созданных объектов Stock в случае успеха.

    Генерирует исключения:
        - RequestException: Если возникла проблема с запросом к API рынка.
        - ValidationError: Если возникла ошибка валидации при создании экземпляра Stock.
        - IntegrityError: Если возникла ошибка целостности при массовом создании экземпляров Stock.
        - Exception: Для любых непредвиденных ошибок.
    """

    logger.info('Начало загрузки доступных акций')
    _start_time = perf_counter()

    try:
        stocks: list[dict] = Market('stocks').tickers(use_dataframe=False)
        logger.info(f'{type(stocks)} {stocks=}')
    except RequestException as error:
        logger.error(f'Произошла ошибка RequestException: {error}', exc_info=True)
        raise
    except Exception as error:
        logger.error(f'Произошла непредвиденная ошибка: {error}', exc_info=True)
        raise
    else:
        logger.debug(f'Информация о акциях получена успешно. {stocks=}')

    stock_objects = []
    for stock in stocks:
        logger.info(f'{type(stock)} {stock=}')
        try:
            stock_objects.append(Stock(
                ticker=stock.get('SECID'),
                shortname=stock.get('SHORTNAME'),
                secname=stock.get('SECNAME'),
                latname=stock.get('LATNAME'),
                prevprice=stock.get('PREVPRICE'),
                lotsize=stock.get('LOTSIZE'),
                facevalue=stock.get('FACEVALUE'),
                faceunit=stock.get('FACEUNIT'),
                status=stock.get('STATUS'),
                decimals=stock.get('DECIMALS'),
                minstep=stock.get('MINSTEP'),
                prevdate=stock.get('PREVDATE'),
                issuesize=stock.get('ISSUESIZE'),
                isin=stock.get('ISIN'),
                regnumber=stock.get('REGNUMBER'),
                prevlegalcloseprice=stock.get('PREVLEGALCLOSEPRICE'),
                currencyid=stock.get('CURRENCYID'),
                sectype=stock.get('SECTYPE'),
                listlevel=stock.get('LISTLEVEL'),
                settledate=stock.get('SETTLEDATE'),
            ))
        except ValidationError as error:
            logger.error(f'Произошла ошибка ValidationError для {stock=}: {error}', exc_info=True)
            raise
        except Exception as error:
            logger.error(f'Произошла ошибка при создании экземпляра Stock с {stock=}: {error}',
                         exc_info=True)
            raise
        else:
            logger.debug(f'Экземпляр Stock успешно создан: stock={stock_objects[-1]}')

    try:
        Stock.objects.bulk_create(
            stock_objects,
            update_conflicts=True,
            unique_fields=['ticker'],
            update_fields=[
                'shortname', 'secname', 'latname', 'prevprice', 'lotsize', 'facevalue', 'faceunit',
                'status', 'decimals', 'minstep', 'prevdate', 'issuesize', 'isin', 'regnumber',
                'prevlegalcloseprice', 'currencyid', 'sectype', 'listlevel', 'settledate', 'updated',
            ],
        )
    except IntegrityError as error:
        logger.error(f'Произошла ошибка целостности при массовом создании: {error}', exc_info=True)
        raise
    except Exception as error:
        logger.error(f'Произошла ошибка при массовом создании: {error}', exc_info=True)
        raise

    loaded = len(stock_objects)
    logger.info(f'{loaded} записей о акциях успешно загружено за {perf_counter() - _start_time}с')
    return loaded


@app.task
def load_latest_historical_data(days: int = 1) -> celery.group:
    """
    Запускает и возвращает группу задач для загрузки исторических данных для всех акций.

    Параметры:
        - days (int): Количество дней, для которых должны быть загружены исторические данные.
            По умолчанию равно 1, что означает загрузку данных за предыдущий день.

    Возвращает:
        - celery.group: Группа задач для загрузки исторических данных за указанный период.
    """

    days = days if days >= 1 else 1

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    return load_historical_data(start_date, end_date)


@app.task
def load_historical_data(start_date: date = None, end_date: date = None) -> celery.group:
    """
    Запускает и возвращает группу задач для загрузки исторических данных для всех акций.

    Параметры:
        - start_date (date или None): Дата начала для загрузки исторических данных.
            По умолчанию None, что означает загрузку с самой ранней доступной даты.
        - end_date (date или None): Дата окончания для загрузки исторических данных.
            По умолчанию None, что означает загрузку до самой поздней доступной даты.

    Возвращает:
        - celery.group: Группа задач для загрузки исторических данных за указанный период.
    """

    stocks = Stock.objects.all().values('ticker')
    tasks_group = celery.group(
        load_historical_data_for_ticker.si(stock['ticker'], start_date, end_date)
        for stock in stocks
    )

    return tasks_group


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 10})
def load_historical_data_for_ticker(ticker: str, start_date: date = None, end_date: date = None) -> int:
    """
    Загружает исторические данные для конкретной акции, создавая объекты Candle и сохраняя их в базе данных.

    Параметры:
        - ticker (str): Тикер акции, для которой должны быть загружены исторические данные.
        - start_date (date или None): Дата начала для загрузки исторических данных.
            По умолчанию None, что означает загрузку с самой ранней доступной даты.
        - end_date (date или None): Дата окончания для загрузки исторических данных.
            По умолчанию None, что означает загрузку до самой поздней доступной даты.

    Возвращает:
        - int: Количество созданных объектов Candle.

    Исключения:
        - Stock.DoesNotExist: Если акция с заданным тикером не существует.
        - IntegrityError: Если произошла ошибка целостности при массовом создании объектов Candle.
        - ValidationError: Если возникла ошибка валидации при создании объектов Candle.
        - Exception: Для любых других неожиданных ошибок в процессе.
    """

    logger.info(f'Начало загрузки исторических данных для {ticker=}')
    _start_time = perf_counter()
    created_candles = 0

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist as error:
        logger.error(f'Акция с тикером {ticker=} не существует: {error}', exc_info=True)
        raise Retry(exc=error, when=None)

    dates = get_available_dates(ticker)

    if dates is None:
        logger.error(f'Не удалось получить доступные даты для {ticker=}')
        return created_candles

    from_, till = dates

    if start_date is not None and end_date is not None:
        num_of_days = (end_date - start_date).days

        end_date = end_date if from_ < end_date <= till else till
        start_date = start_date if from_ <= start_date < end_date else end_date - timedelta(days=num_of_days)
    elif start_date is not None:
        start_date = start_date if from_ <= start_date < end_date else from_
        end_date = till
    elif end_date is not None:
        end_date = end_date if from_ < end_date <= till else till
        start_date = from_
    else:
        start_date, end_date = from_, till

    try:
        for candle_objects in load_candles(ticker, start_date, end_date):
            created = Candle.objects.bulk_create(
                [Candle(
                    stock=stock,
                    open=candle.open,
                    close=candle.close,
                    high=candle.high,
                    low=candle.low,
                    value=candle.value,
                    volume=candle.volume,
                    time_range=DateTimeRange(candle.begin, candle.end)
                )
                    for candle in candle_objects],
                ignore_conflicts=True,
            )
            created_candles += len(created)
    except IntegrityError as error:
        logger.error(f'Ошибка целостности для {ticker=}: {error}', exc_info=True)
        raise
    except ValidationError as error:
        logger.error(f'Ошибка валидации для {ticker=}: {error}', exc_info=True)
        raise
    except Exception as error:
        logger.error(f'Ошибка при создании экземпляра Candle или массовом создании для {ticker=}: {error}',
                     exc_info=True)
        raise
    else:
        logger.info(
            f'{created_candles} записей исторических данных для {ticker=} успешно загружены за {perf_counter() - _start_time}s')
        return created_candles


@app.task
def load_price_changes() -> celery.group:
    """
    Запускает и возвращает группу задач для загрузки изменений цен для всех акций.

    Возвращает:
        - celery.group: Группа задач для загрузки изменений цен для всех акций.
    """

    stocks = Stock.objects.all().values('ticker')
    tasks_group = celery.group(
        load_price_changes_for_ticker.si(stock['ticker'])
        for stock in stocks
    )

    return tasks_group


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 10})
def load_price_changes_for_ticker(ticker: str) -> None:
    """
    Загружает изменения цен для конкретной акции по тикеру.

    Параметры:
        - ticker (str): Тикер акции.

    Исключения:
        - Retry: Если акция с указанным тикером не существует.
        - Exception: Для любых других неожиданных ошибок в процессе.

    Возвращает:
        - None
    """

    logger.info(f'Начало загрузки изменений цен для {ticker=}')
    _start_time = perf_counter()

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist as error:
        logger.error(f'Акция с тикером {ticker=} не существует: {error}', exc_info=True)
        raise Retry(exc=error, when=None)

    try:
        value_per_day, percent_per_day = calculate_price_change_per_day(stock)
        value_per_year, percent_per_year = calculate_price_change_per_year(stock)

        price_change, _ = PriceChange.objects.get_or_create(
            stock=stock,
            defaults={
                'value_per_day': 0,
                'percent_per_day': 0,
                'value_per_year': 0,
                'percent_per_year': 0,
            },
        )

        price_change.value_per_day = value_per_day
        price_change.percent_per_day = percent_per_day
        price_change.value_per_year = value_per_year
        price_change.percent_per_year = percent_per_year

        price_change.save()
    except Exception as error:
        logger.error(f'Произошла непредвиденная ошибка: {error}', exc_info=True)
        raise

    logger.info(f'Изменения цен для {ticker=} успешно загружены за {perf_counter() - _start_time}s')
