from django import template

from decimal import Decimal

register = template.Library()


@register.filter
def normalize(value: Decimal | float, args: str = None) -> str:
    """
    The normalize filter is used to format the Decimal or float number
    by removing the extra zeros to the right of the decimal point.

    Parameters:
        - value (Decimal or float): The Decimal or float number that needs to be formatted.
        - args (str, optional): A string containing additional arguments for formatting.
          Arguments should be provided in the format "key1=value1,key2=value2,...".
          Supported arguments:
              - places (int): The number of decimal places to preserve.
                If provided, the resulting number will be formatted with the specified number of decimal places.
                If omitted, trailing zeros will be removed without adjusting the number of decimal places.
              - minus (bool): Specifies whether to preserve the minus sign for negative values.
                If True, the minus sign will be preserved. If False, the minus sign will be removed.
                Defaults to True.

    Returns:
        - str: A formatted string representing the number without any trailing zeros to
          the right of the decimal point, if applicable. Otherwise, it returns the original value
          converted to a string. If the value is None, the function returns a dash ('-') to represent
          missing or undefined data.
    
    Usage example:
        - {{ stock.prevprice|normalize }}
          This will display the previous price of the stock with any trailing zeros removed.
        - {{ price|normalize:'places=2' }}
          This will display the price with two decimal places, removing any trailing zeros beyond that.
        - {{ percent_per_day|normalize:'places=2,minus=False' }}
          This will display the percent change per day with two decimal places,
          removing any trailing zeros beyond that, and without preserving the minus sign for negative values.
    """

    if value is None:
        return '-'
    
    kwargs = {}
    if args is not None and isinstance(args, str):
        for arg in args.split(','):
            k, v = arg.split('=')
            kwargs[k] = v

    places = int(kwargs.get('places', -1))
    minus = kwargs.get('minus', 'True') == 'True'

    if isinstance(value, Decimal | float):
        if places > -1:
            value = round(value, places)
        value = str(value).rstrip('0').rstrip('.')

        return value if minus else value.lstrip('-')

    return value


@register.filter
def convert_currency_code(value: str) -> str:
    """
    The convert_currency_code filter is used to convert the
    currency code to the appropriate currency symbol.

    Parameters:
        -  value (str): The currency code that you want to convert to a symbol.

    Returns:
        - str: The currency symbol corresponding to the input code.
        If the currency code is missing from the currency_codes dictionary,
        the original value is returned.
    
    Usage example:
        - {{ currency_code|convert_currency_code }}
    """

    currency_codes = {
        'SUR': '₽',
    }

    if isinstance(value, str):
        return currency_codes.get(value, value)
        
    return value