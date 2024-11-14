from datetime import date, timedelta
from time import perf_counter
from typing import Generator

import requests
from django.utils import timezone
from loguru import logger
from moexalgo import Ticker
from requests import RequestException

from ..models import Stock

_BASE_URL = 'http://iss.moex.com/iss'
_HISTORY_SECURITIES_URL = _BASE_URL + '/history/engines/stock/markets/shares/boards/TQBR/securities'

DATES_URL = _HISTORY_SECURITIES_URL + '/{ticker}/dates.json'


def get_available_dates(ticker: str) -> tuple[date, date] | None:
    """
    Получает доступные даты для указанного тикера.

    Параметры:
        - ticker (str): Символ тикера, для которого нужно получить даты.

    Возвращает:
        - tuple[date, date] или None: Кортеж, содержащий начальную и конечную даты, если запрос успешен, иначе None.
    """

    logger.info(f'Начало получения доступных дат для {ticker=}')
    _start_time = perf_counter()

    try:
        response = requests.get(DATES_URL.format(ticker=ticker))
        data = response.json()
        start_date, end_date = data['dates']['data'][0]
        start_date, end_date = date.fromisoformat(start_date), date.fromisoformat(end_date)
    except requests.RequestException as error:
        logger.error(f'Произошла ошибка RequestException для {ticker=}: {error}', exc_info=True)
    except KeyError as error:
        logger.error(f'Произошла ошибка KeyError для {ticker=}: {error}', exc_info=True)
    except IndexError as error:
        logger.error(f'Произошла ошибка IndexError для {ticker=}: {error}', exc_info=True)
    except TypeError as error:
        logger.error(f'Произошла ошибка TypeError для {ticker=}: {error}', exc_info=True)
    except ValueError as error:
        logger.error(f'Произошла ошибка ValueError для {ticker=}: {error}', exc_info=True)
    except Exception as error:
        logger.error(f'Произошла непредвиденная ошибка для {ticker=}: {error}', exc_info=True)
    else:
        logger.info(f'Доступные даты для {ticker=} успешно получены за {perf_counter() - _start_time}с')
        return start_date, end_date

    return None


def load_candles(ticker: str, start_date: date, end_date: date) -> Generator[Generator, None, None]:
    """
    Функция-генератор для загрузки свечей для указанного тикера в определенном диапазоне дат.

    Параметры:
        - ticker (str): Символ тикера, для которого нужно загрузить свечи.
        - start_date (date): Начальная дата диапазона.
        - end_date (date): Конечная дата диапазона.

    Возвращает:
        - Generator: Генерирует данные свечей для каждого периода в указанном диапазоне.

    Возвращает:
        - None: Возвращает None после завершения.
    """

    logger.info(f'Начало загрузки свечей для {ticker=}')
    _start_time = perf_counter()

    try:
        ticker_obj = Ticker(ticker)
    except RequestException as error:
        logger.error(f'Произошла ошибка RequestException для {ticker=}: {error}', exc_info=True)
        return None
    except Exception as error:
        logger.error(f'Произошла непредвиденная ошибка для {ticker=}: {error}', exc_info=True)
        return None
    else:
        logger.debug(f'Информация о {ticker=} успешно получена')

    try:
        logger.debug(f'Начало обработки свечей для {ticker=}')
        while start_date < end_date:
            till_date = start_date + timedelta(days=365)
            candles: Generator = ticker_obj.candles(start=start_date, end=till_date, use_dataframe=False)
            yield candles
            start_date = till_date
    except RequestException as error:
        logger.error(f'Произошла ошибка RequestException для {ticker=}: {error}', exc_info=True)
        return None
    except Exception as error:
        logger.error(f'Произошла непредвиденная ошибка для {ticker=}: {error}', exc_info=True)
        return None
    else:
        logger.debug(f'Обработка свечей для {ticker=} завершена успешно')

    logger.info(f'Свечи для {ticker=} успешно загружены за {perf_counter() - _start_time}с')
    return None


def calculate_price_change(stock: Stock, days: int) -> tuple[int | float, int | float]:
    """
    Рассчитывает изменение цены акции за заданное количество дней.

    Параметры:
        - stock (Stock): Акция, для которой необходимо рассчитать изменение цены.
        - days (int): Количество дней, за которое необходимо рассчитать изменение цены.

    Возвращает:
        - Tuple[int | float, int | float]: Кортеж, содержащий изменение цены и процентное изменение.
        Если нет данных за указанный период времени, возвращается (0, 0).
    """

    tz_now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_days = tz_now - timedelta(days=days)
    candles_per_days = stock.candles.filter(time_range__overlap=[last_days, tz_now + timedelta(days=1)]).order_by(
        'time_range')

    if candles_per_days.exists():
        first_open = candles_per_days.first().open
        last_close = candles_per_days.last().close
        price_change = last_close - first_open

        if first_open != 0:
            percent_change = (price_change / first_open) * 100

            price_change = 0 if price_change == -0 else price_change
            percent_change = 0 if percent_change == -0 else percent_change

            return price_change, percent_change

    return 0, 0


def calculate_price_change_per_day(stock: Stock):
    """
    Рассчитывает изменение цены за один день для заданной акции.

    Параметры:
        - stock (Stock): Акция, для которой необходимо рассчитать изменение цены за один день.

    Возвращает:
        - Tuple[int | float, int | float]: Кортеж, содержащий изменение цены и процентное изменение.
        Если нет данных за указанный период времени, возвращается (0, 0).
    """

    return calculate_price_change(stock, 1)


def calculate_price_change_per_year(stock: Stock):
    """
    Рассчитывает изменение цены за год для заданной акции.

    Параметры:
        - stock (Stock): Акция, для которой необходимо рассчитать изменение цены за год.

    Возвращает:
        - Tuple[int | float, int | float]: Кортеж, содержащий изменение цены и процентное изменение.
        Если нет данных за указанный период времени, возвращается (0, 0).
    """

    return calculate_price_change(stock, 365)
