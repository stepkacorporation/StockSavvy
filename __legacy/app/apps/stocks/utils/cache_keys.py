"""
Constants for key names and default timeout values used in
stock-related operations for caching purposes.
"""

DEFAULT_TIMEOUT = 60 * 60 * 24  # 1 day

LAST_PRICE_KEY = 'last_price_' + '{ticker}'
LAST_CANDLE_DATE_KEY = 'last_candle_date_' + '{ticker}'
DAILY_PRICE_RANGE_KEY = 'daily_price_range_' + '{ticker}'
YEARLY_PRICE_RANGE_KEY = 'yearly_price_range_' + '{ticker}'
OPENING_CLOSING_PRICE_TODAY_KEY = 'opening_closing_price_today_' + '{ticker}'

STOCK_DETAIL_KEY = 'stock_detail_{ticker}'
