from django import template

from decimal import Decimal

register = template.Library()


@register.simple_tag
def normalize(value: Decimal | float, places: int = -1, plus: bool = False, minus: bool = True) -> str:
    """
    The normalize filter is used to format the Decimal or float number
    by removing the extra zeros to the right of the decimal point.

    Parameters:
        - value (Decimal or float): The Decimal or float number that needs to be formatted.
        - places (int, optional): The number of decimal places to preserve.
          If provided, the resulting number will be formatted with the specified number of decimal places.
          If omitted, trailing zeros will be removed without adjusting the number of decimal places.
          Defaults to -1.
        - plus (bool, optional): Specifies whether to prepend a plus sign for positive values.
          If True, a plus sign will be added for positive values. If False, no plus sign will be added.
          Defaults to False.
        - minus (bool, optional): Specifies whether to preserve the minus sign for negative values.
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
    
    if isinstance(value, Decimal | float):
        if value == 0:
            return 0
        
        if places > -1:
            value = round(value, places)
        
        _num_value = value

        value = str(value)
        if '.' in value:
            value = value.rstrip('0').rstrip('.')
        value = value if minus else value.lstrip('-')
        value = f'+{value}' if plus and _num_value > 0 else value

    return value


@register.filter
def convert_currency_code(value: str, in_symbol: bool = True) -> str:
    """
    The convert_currency_code filter is used to convert the
    currency code to the appropriate currency symbol or text representation.

    Parameters:
        - value (str): The currency code that you want to convert to a symbol or text.
        - in_symbol (bool, optional): Specifies whether to return the currency symbol.
          If True, the function returns the currency symbol corresponding to the input code.
          If False, the function returns the text representation of the currency code.
          Defaults to True.

    Returns:
        - str: The currency symbol or text corresponding to the input code.
          If the currency code is missing from the currency codes dictionary,
          the original value is returned.
    
    Usage example:
        - {{ currency_code|convert_currency_code }}
          This will display the currency symbol corresponding to the currency code.
        - {{ currency_code|convert_currency_code:False }}
          This will display the text representation of the currency code.
    """

    currency_codes_in_symbols = {
        'SUR': '₽',
    }

    currency_codes_in_text = {
        'SUR': 'RUB',
    }

    if isinstance(value, str):
        if in_symbol:
            return currency_codes_in_symbols.get(value, value)
        return currency_codes_in_text.get(value, value)

    return value