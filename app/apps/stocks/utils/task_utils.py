import requests

from moexalgo import Ticker
from datetime import date, timedelta
from time import perf_counter
from requests import RequestException
from celery.utils.log import get_task_logger
from typing import Generator

from config.celery import add_file_logger

logger = add_file_logger(get_task_logger(__name__))

_BASE_URL = 'http://iss.moex.com/iss'
_HISTORY_SECURITIES_URL = _BASE_URL + '/history/engines/stock/markets/shares/boards/TQBR/securities'

DATES_URL = _HISTORY_SECURITIES_URL + '/{ticker}/dates.json'


def get_available_dates(ticker: str) -> tuple[date, date] | None:
    """
    Retrieves the available dates for a given ticker.

    Parameters:
        - ticker (str): The ticker symbol for which to get dates.

    Returns:
        - tuple[date, date] or None: A tuple containing the start and end dates if successful, None otherwise.
    """

    logger.info(f'The start of getting available dates for the {ticker=}')
    _start_time = perf_counter()

    try:
        response = requests.get(DATES_URL.format(ticker=ticker))
        data = response.json()
        start_date, end_date = data['dates']['data'][0]
        start_date, end_date = date.fromisoformat(start_date), date.fromisoformat(end_date)
    except requests.RequestException as error:
        logger.error(f'RequestException occurred for {ticker=}: {error}', exc_info=True)
    except KeyError as error:
        logger.error(f'KeyError occurred for {ticker=}: {error}', exc_info=True)
    except IndexError as error:
        logger.error(f'IndexError occurred for {ticker=}: {error}', exc_info=True)
    except TypeError as error:
        logger.error(f'TypeError occurred for {ticker=}: {error}', exc_info=True)
    except ValueError as error:
        logger.error(f'ValueError occurred for {ticker=}: {error}', exc_info=True)
    except Exception as error:
        logger.error(f'An unexpected error occurred for {ticker=}: {error}', exc_info=True)
    else:
        logger.info(f'The available dates for the {ticker=} have been'
                    f' successfully received in {perf_counter() - _start_time}s')
        return start_date, end_date

    return None


def load_candles(ticker: str, start_date: date, end_date: date) -> Generator[Generator, None, None]:
    """
    Generator function to load candles for a given ticker within a specified date range.

    Parameters:
        - ticker (str): The ticker symbol for which to load candles.
        - start_date (date): The start date of the date range.
        - end_date (date): The end date of the date range.

    Yields:
        - Generator: Yields candle data for each period within the specified range.

    Returns:
        - None: Returns None upon completion.
    """

    logger.info(f'The start of loading candles for the {ticker=}')
    _start_time = perf_counter()

    try:
        ticker_obj = Ticker(ticker)
    except RequestException as error:
        logger.error(f'RequestException occurred for {ticker=}: {error}', exc_info=True)
        return None
    except Exception as error:
        logger.error(f'An unexpected error occurred for {ticker=}: {error}', exc_info=True)
        return None
    else:
        logger.debug(f'Information about {ticker=} has been successfully received')

    try:
        logger.debug(f'The start of candle processing for the {ticker=}')
        while start_date < end_date:
            till_date = start_date + timedelta(days=365)
            candles: Generator = ticker_obj.candles(date=start_date, till_date=till_date)
            yield candles
            start_date = till_date
    except RequestException as error:
        logger.error(f'RequestException occurred for {ticker=}: {error}', exc_info=True)
        return None
    except Exception as error:
        logger.error(f'An unexpected error occurred for {ticker=}: {error}', exc_info=True)
        return None
    else:
        logger.debug(f'The candle processing for the {ticker=} has been completed successfully')

    logger.info(f'Candles for the {ticker=} have been successfully loaded in {perf_counter() - _start_time}s')
    return None
