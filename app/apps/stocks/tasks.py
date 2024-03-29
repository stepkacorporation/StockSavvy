from django.db import IntegrityError
from django.core.exceptions import ValidationError
from celery.utils.log import get_task_logger
from moexalgo import Market
from requests.exceptions import RequestException
from time import perf_counter

from config.celery import app, add_file_logger
from .models import Stock

logger = add_file_logger(get_task_logger(__name__))


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 10})
def load_available_stocks() -> int:
    """
    Loads available stocks from the market and creates or updates Stock objects in the database.

    Returns:
         int: The number of Stock objects created in case of success.

    Raises:
        RequestException: If there is an issue with the request to the market API.
        ValidationError: If there is a validation error while creating a Stock instance.
        IntegrityError: If there is an integrity error during bulk creation of Stock instances.
        Exception: For any unexpected errors.
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
