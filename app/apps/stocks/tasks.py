import celery

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import DateTimeRange
from celery.utils.log import get_task_logger
from celery.result import GroupResult
from moexalgo import Market
from requests.exceptions import RequestException
from time import perf_counter
from datetime import date, timedelta

from config.celery import app, add_file_logger
from .utils.task_utils import get_available_dates, load_candles
from .models import Stock, Candle

logger = add_file_logger(get_task_logger(__name__))


def load_stock_data() -> None:
    """
    Runs tasks to load available stocks and
    historical data for all loaded available stocks.

    Returns:
        - None
    """

    logger.info('The start of load stock data')
    _start_time = perf_counter()

    loaded_available_stocks = load_available_stocks.delay()
    loaded_available_stocks.get()  # Waiting for the result of loading the available stocks

    load_historical_data_tasks_group = load_historical_data()
    load_historical_data_tasks_group.join()  # Waiting for the result of loading historical data for all stocks

    logger.info(f'Stock data has been successfully loaded in {perf_counter() - _start_time}s')


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 10})
def load_available_stocks() -> int:
    """
    Loads available stocks from the market and creates or updates Stock objects in the database.

    Returns:
        - int: The number of Stock objects created in case of success.

    Raises:
        - RequestException: If there is an issue with the request to the market API.
        - ValidationError: If there is a validation error while creating a Stock instance.
        - IntegrityError: If there is an integrity error during bulk creation of Stock instances.
        - Exception: For any unexpected errors.
    """

    logger.info('The start of load available stocks')
    _start_time = perf_counter()

    try:
        stocks: list[dict] = Market('stocks').tickers()
    except RequestException as error:
        logger.error(f'RequestException occurred: {error}', exc_info=True)
        raise
    except Exception as error:
        logger.error(f'An unexpected error occurred: {error}', exc_info=True)
        raise
    else:
        logger.debug(f'Information about the stocks was received successfully. {stocks=}')

    stock_objects = []
    for stock in stocks:
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
            logger.error(f'ValidationError occurred for {stock=}: {error}', exc_info=True)
            raise
        except Exception as error:
            logger.error(f'An error occurred while creating a Stock instance with {stock=}: {error}',
                         exc_info=True)
            raise
        else:
            logger.debug(f'A Stock instance has been successfully created: stock={stock_objects[-1]}')

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
        logger.error(f'Integrity error occurred during bulk creation: {error}', exc_info=True)
        raise
    except Exception as error:
        logger.error(f'An error occurred during bulk creation: {error}', exc_info=True)
        raise

    loaded = len(stock_objects)
    logger.info(f'{loaded} stock records have been successfully loaded in {perf_counter() - _start_time}s')
    return loaded


@app.task
def load_latest_historical_data(days: int = 1) -> None:
    """
    Loads historical data for the latest specified number of days.

    Parameters:
        - days (int): The number of days for which historical data should be loaded. 
            Defaults to 1, meaning loading data for the previous day.

    Returns:
        - None
    """
    
    days = days if days >= 1 else 1

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    load_historical_data.delay(start_date, end_date)


@app.task
def load_historical_data(start_date: date = None, end_date: date = None) -> GroupResult:
    """
    Starts and returns a task group to load historical data for all stocks.

    Parameters:
        - start_date (date or None): The start date for loading historical data. 
            Defaults to None, meaning loading from the earliest available date.
        - end_date (date or None): The end date for loading historical data.
            Defaults to None, meaning loading until the latest available date.

    Returns:
        - GroupResult: The result of executing the group task.
    """
    
    stocks = Stock.objects.all()
    tasks_group = celery.group(load_historical_data_for_ticker.s(stock.ticker, start_date, end_date) for stock in stocks)()
    return tasks_group


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 10})
def load_historical_data_for_ticker(ticker: str, start_date: date = None, end_date: date = None) -> int:
    """
    Loads historical data for a specific stock by creating Candle objects and storing them in the database.

    Parameters:
        - ticker (str): The ticker symbol for which historical data is to be loaded.
        - start_date (date or None): The start date for loading historical data. 
            Defaults to None, meaning loading from the earliest available date.
        - end_date (date or None): The end date for loading historical data.
            Defaults to None, meaning loading until the latest available date.

    Returns:
        - int: The number of Candle objects created.

    Raises:
        - Stock.DoesNotExist: If the stock with the given ticker does not exist.
        - IntegrityError: If there is an integrity violation while creating Candle objects in bulk.
        - ValidationError: If there is a validation error while creating Candle objects.
        - Exception: For any other unexpected error during the process.
    """

    logger.info(f'The start of load historical data for {ticker=}')
    _start_time = perf_counter()
    created_candles = 0

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist as error:
        logger.error(f'Stock with {ticker=} does not exist: {error}', exc_info=True)
        raise

    dates = get_available_dates(ticker)

    if dates is None:
        logger.error(f'Could not get available dates for {ticker=}')
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
        logger.error(f'Integrity error occurred for {ticker=}: {error}', exc_info=True)
        raise
    except ValidationError as error:
        logger.error(f'ValidationError occurred for {ticker=}: {error}', exc_info=True)
        raise
    except Exception as error:
        logger.error(f'An error occurred while creating a Candle instance'
                     f' or during bulk creation for {ticker=}: {error}', exc_info=True)
        raise
    else:
        logger.info(f'{created_candles} historical data records for the {ticker=} has been'
                    f' successfully loaded in {perf_counter() - _start_time}s')
        return created_candles
