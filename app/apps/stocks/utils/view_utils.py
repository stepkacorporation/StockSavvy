from django.template.response import TemplateResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from datetime import timedelta

from apps.accounts.models import User

from ..models import Favourite, Stock, PriceChange
from ..templatetags.formatting_filters import normalize
from ..utils.cache_utils import DAILY_PRICE_RANGE_KEY, YEARLY_PRICE_RANGE_KEY


def add_favourite_stocks_to_context(context: dict, user: User) -> dict:
    """
    Adds the user's favourite stocks to the context dictionary if the user is authenticated.

    Parameters:
        - context (dict): A dictionary representing the context of the request.
        - user (User): The user object for whom to retrieve favourite stocks.

    Returns:
        - dict: The context dictionary with the 'favourite_stocks' key
        containing the user's favourite stock tickers.
    """

    if user.is_authenticated:
        favourite_stocks = Favourite.objects.filter(user=user).values_list('stock__ticker', flat=True)
        context['favourite_stocks'] = favourite_stocks
    
    return context


def set_no_cache(response: TemplateResponse) -> TemplateResponse:
    """
    Sets the Cache-Control, Pragma, and Expires headers in the response to disable caching.

    Args:
        - response (TemplateResponse): TemplateResponse object to modify.

    Returns:
        - TemplateResponse: Modified TemplateResponse object with caching disabled.
    """

    response["Cache-Control"] = "no-cache, no-store, must-revalidate"  # HTTP 1.1.
    response["Pragma"] = "no-cache"  # HTTP 1.0.
    response["Expires"] = "0"  # Proxies.
    return response


def get_price_info(stock: Stock, decimals: int, currency: str, per: str = 'day') -> tuple:
    """
    Retrieves price information for a stock.

    Args:
        - stock (Stock): The stock object for which to retrieve price information.
        - decimals (int): The number of decimal places to round the values.
        - currency (str): The currency in which the prices are displayed.
        - per (str): The time period for which to retrieve the price information (default is 'day').

    Returns:
        - tuple: A tuple containing the value, percent change, and formatted change information.
    """

    normalized_value, normalized_percent, change = None, None, None
    
    try:
        stock_price_change: PriceChange = stock.price_change
    except ObjectDoesNotExist:
        return 0, 0, change

    days_offset = (365, 1)[per == 'day'] 
    updated_date = stock_price_change.updated.replace(hour=0, minute=0, second=0, microsecond=0)
    current_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if updated_date < current_date - timedelta(days=days_offset):
        return 0, 0, change

    try:
        if per == 'day':
            value = stock_price_change.value_per_day
            percent = stock_price_change.percent_per_day
        else:
            value = stock_price_change.value_per_year
            percent = stock_price_change.percent_per_year
    except ObjectDoesNotExist:
        return 0, 0, change

    if value is not None and percent is not None:
        normalized_value = normalize(value, places=decimals, plus=True)
        normalized_percent = normalize(percent, places=2, minus=False)
        change = f'{normalized_value} {currency} ({normalized_percent}%)'
    
    return value, percent, change


def get_price_range(stock: Stock, decimals: int, currency: str, per: str = 'day') -> str:
    """
    Calculate and return the price range for a given stock.

    Args:
        - stock (Stock): The stock object for which to calculate price range.
        - decimals (int): The number of decimal places to round the values.
        - currency (str): The currency in which the prices are displayed.
        - per (str): The time period for which to calculate the price change (default is 'day').

    Returns:
        - str: A string representing the calculated price range in the format
        '{min_price} {currency} - {max_price} {currency}'.
    """
    
    price_range = '-'
    _ticker = stock.ticker

    if per == 'day':
        cache_key = DAILY_PRICE_RANGE_KEY.format(ticker=_ticker)
        min_price, max_price = stock.get_price_range(days_offset=0, cache_key=cache_key)
    else:
        cache_key = YEARLY_PRICE_RANGE_KEY.format(ticker=_ticker)
        min_price, max_price = stock.get_price_range(days_offset=365, cache_key=cache_key)
    
    if min_price is not None and max_price is not None:
        normalized_min_price = normalize(min_price, places=decimals)
        normalized_max_price = normalize(max_price, places=decimals)
        price_range = f'{normalized_min_price} {currency} - {normalized_max_price} {currency}'

    return price_range


