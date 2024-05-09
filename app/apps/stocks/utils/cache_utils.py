from django.core.cache import cache

from .cache_keys import (
    LAST_PRICE_KEY,
    LAST_CANDLE_DATE_KEY,
    DAILY_PRICE_RANGE_KEY,
    YEARLY_PRICE_RANGE_KEY,
    OPENING_CLOSING_PRICE_TODAY_KEY,
    STOCK_DETAIL_KEY,
)
from ..models import Stock


def clear_stock_cache() -> None:
    """
    Clears the cache entries for all stock tickers.

    Returns:
        - None
    """

    tickers = Stock.objects.values_list('ticker', flat=True)
    for ticker in tickers:
        clear_stock_cache_for_ticker(ticker)


def clear_stock_cache_for_ticker(ticker: str) -> None:
    """
    Clears the cache entries for a specific stock ticker.

    Args:
        ticker (str): The stock ticker for which cache entries need to be cleared.
    
    Returns:
        - None
    """

    keys_to_clear = [
        LAST_PRICE_KEY.format(ticker=ticker),
        LAST_CANDLE_DATE_KEY.format(ticker=ticker),
        DAILY_PRICE_RANGE_KEY.format(ticker=ticker),
        YEARLY_PRICE_RANGE_KEY.format(ticker=ticker),
        OPENING_CLOSING_PRICE_TODAY_KEY.format(ticker=ticker),
        STOCK_DETAIL_KEY.format(ticker=ticker),
    ]
    for key in keys_to_clear:
        cache.delete(key)