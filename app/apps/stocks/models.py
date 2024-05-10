from django.db import models
from django.db.models import Min, Max
from django.urls import reverse
from django.utils import timezone
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.auth import get_user_model
from django.core.cache import cache

from datetime import timedelta, datetime
from decimal import Decimal

from .managers import StockManager
from .utils.cache_keys import (
    DEFAULT_TIMEOUT,
    LAST_PRICE_KEY,
    LAST_CANDLE_DATE_KEY,
    OPENING_CLOSING_PRICE_TODAY_KEY,
)

User = get_user_model()


class Stock(models.Model):
    """
    Represents a financial instrument (stock).
    """

    class StatusChoices(models.TextChoices):
        """
        The status of a financial instrument.

        Docs:
        https://ftp.moex.com/pub/ClientsAPI/ASTS/Bridge_Interfaces/Equities/Equities36_Broker_Russian.htm#eTSecStatus
        """

        A = 'A', 'Operations are allowed'
        S = 'S', 'Operations are prohibited'
        N = 'N', 'Blocked for trading, execution of transactions is allowed'

    class SecTypeChoices(models.TextChoices):
        """
        Types of securities.

        Docs:
        http://ftp.moex.ru/pub/ClientsAPI/ASTS/Bridge_Interfaces/MarketData/Equities31_Info_Russian.htm#eTSecType
        """

        FIRST = '1', 'The security is ordinary'
        SECOND = '2', 'The security is privileged'
        THIRD = '3', 'Government bonds'
        FOURTH = '4', 'Regional bonds'
        FIFTH = '5', 'Central bank bonds'
        SIXTH = '6', 'Corporate bonds'
        SEVENTH = '7', 'MFO bonds'
        EIGHTH = '8', 'Exchange-traded bonds'
        NINTH = '9', 'Shares of open MIF'
        A = 'A', 'Shares of interval MIF'
        B = 'B', 'Shares of closed MIF'
        C = 'C', 'Municipal bonds'
        D = 'D', 'Depository receipts'
        E = 'E', 'Securities of exchange investment funds (ETFs)'
        F = 'F', 'Mortgage certificate'
        G = 'G', 'A basket of securities'
        H = 'H', 'Additional list ID'
        I = 'I', 'ETC (commodity instruments)'
        U = 'U', 'Clearing certificates of participation'
        Q = 'Q', 'Currency'
        J = 'J', 'A share of stock exchange MIF'

    class ListLevelChoices(models.IntegerChoices):
        """
        The listing levels.
        """

        FIRST = 1, 'First'
        SECOND = 2, 'Second'
        THIRD = 3, 'Third'

    ticker = models.CharField(
        primary_key=True,
        max_length=10,
        verbose_name='ticker',
        help_text='The ticker of the stock.',
        db_index=True,
    )
    shortname = models.CharField(
        max_length=50,
        verbose_name='short name',
        help_text='The short name of the instrument.',
        null=True,
    )
    secname = models.CharField(
        max_length=50,
        verbose_name='secname',
        help_text='The name of the financial instrument.',
        null=True,
    )
    latname = models.CharField(
        max_length=50,
        verbose_name='latname',
        help_text='The name of the financial instrument in English.',
        null=True,
    )
    prevprice = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=10,
        verbose_name='prevprice',
        help_text='The price of the last trade of the previous day.',
        null=True,
    )
    lotsize = models.PositiveIntegerField(
        verbose_name='lotsize',
        help_text='The number of securities in one standard lot.',
        null=True,
    )
    facevalue = models.DecimalField(
        max_digits=34,
        decimal_places=17,
        verbose_name='facevalue',
        help_text='The nominal value of one security at the current date.',
        null=True,
    )
    faceunit = models.CharField(
        max_length=10,
        verbose_name='faceunit',
        help_text='The code of the currency in which the nominal value of the security is expressed.',
        null=True,
    )
    status = models.CharField(
        max_length=1,
        choices=StatusChoices,
        default=StatusChoices.A,
        verbose_name='status',
        help_text='The indicator "trading operations are allowed/prohibited".',
        null=True,
    )
    decimals = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='decimals',
        help_text='The number of decimal places of the fractional part of the number. '
                  'It is used to format the values of fields with the DECIMAL type.',
        null=True,
    )
    minstep = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        verbose_name='min step',
        help_text='The minimum possible difference between the prices'
                  ' indicated in the bids for the purchase/sale of securities',
        null=True,
    )
    prevdate = models.DateField(verbose_name='prevdate', help_text='The date of the previous trading day.', null=True)
    issuesize = models.PositiveBigIntegerField(
        verbose_name='issuesize',
        help_text='The number of securities in the issue.',
        null=True,
    )
    isin = models.CharField(
        max_length=20,
        verbose_name='isin',
        help_text='The international identification code of the security.',
        null=True,
    )
    regnumber = models.CharField(
        max_length=50,
        verbose_name='regnumber',
        help_text='The number of the state registration.',
        null=True,
    )
    prevlegalcloseprice = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=10,
        verbose_name='prev legal close price',
        help_text="The official closing price of the previous day, calculated in "
                  "accordance with the trading rules as the weighted average price "
                  "of transactions for the last 10 minutes of the main session, including "
                  "transactions of the post-trading period or the closing auction.",
        null=True,
    )
    currencyid = models.CharField(
        max_length=10,
        verbose_name='currency ID',
        help_text='The currency of settlement for the instrument.',
        null=True,
    )
    sectype = models.CharField(
        max_length=1,
        choices=SecTypeChoices,
        default=SecTypeChoices.FIRST,
        verbose_name='sectype',
        help_text='The type of security.',
        null=True,
    )
    listlevel = models.PositiveSmallIntegerField(
        choices=ListLevelChoices,
        default=ListLevelChoices.FIRST,
        verbose_name='listlevel',
        help_text='The listing level.',
        null=True,
    )
    settledate = models.DateField(
        verbose_name='settledate',
        help_text='Settlement date of the transaction.',
        null=True,
    )

    updated = models.DateTimeField(auto_now=True, verbose_name='updated')

    objects = StockManager()

    def __str__(self) -> str:
        return f'{self.shortname} ({self.ticker}) {self.prevprice} {self.currencyid}'

    class Meta:
        verbose_name = 'stock'
        verbose_name_plural = 'stocks'
        ordering = ('ticker',)

    def save(self, *args, **kwargs):
        if self.ticker:
            self.ticker = self.ticker.upper()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('stock-detail', kwargs={'ticker': self.ticker})
    
    def get_opening_and_closing_price_today(self) -> tuple[Decimal, Decimal]:
        """
        Retrieves the opening and closing prices for today's candles.
        
        Returns:
            - tuple: A tuple containing the opening price and closing price for today.
        """

        cache_key = OPENING_CLOSING_PRICE_TODAY_KEY.format(ticker=self.ticker)
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        end_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day = end_of_day - timedelta(days=1)

        today_candles = self.candles.filter(
            time_range__overlap=[start_of_day, end_of_day]
        ).order_by('time_range')
        
        opening_price, closing_price = None, None
        
        if today_candles.exists():
            opening_price = today_candles.first().open
            closing_price = today_candles.last().close

        cache.set(cache_key, (opening_price, closing_price), timeout=DEFAULT_TIMEOUT)

        return opening_price, closing_price
    
    def get_price_range(self, days_offset: int, cache_key: str) -> tuple[Decimal, Decimal]:
        """
        Retrieves the price range for a specified number of days.

        Args:
            - days_offset (int): The number of days to consider for the price range.
            - cache_key (str): The key to cache the data.

        Returns:
            - tuple: A tuple containing the minimum price and maximum price for the specified range of days.
        """
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        end_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day = end_of_day - timedelta(days=1)

        today_candles = self.candles.filter(
            time_range__overlap=[start_of_day - timedelta(days=days_offset), end_of_day + timedelta(days=1)]
        ).order_by('time_range')

        min_price, max_price = None, None

        if today_candles.exists():
            min_price = today_candles.aggregate(min_price=Min('low'))['min_price']
            max_price = today_candles.aggregate(max_price=Max('high'))['max_price']

        cache.set(cache_key, (min_price, max_price), timeout=DEFAULT_TIMEOUT)

        return min_price, max_price

    def get_last_price(self) -> Decimal:
        """
        Retrieves the last price available.

        Returns:
            - Decimal: The last price available.
        """
            
        cache_key = LAST_PRICE_KEY.format(ticker=self.ticker)
        cached_price = cache.get(cache_key)
        if cached_price is not None:
            return cached_price
        
        first_candle = self.candles.first()
        price = first_candle.close if first_candle else None
        cache.set(cache_key, price, timeout=DEFAULT_TIMEOUT)
        return price
    
    def get_last_candle_date(self) -> datetime:
        """
        Retrieves the date of the last candle.

        Returns:
            - datetime: The date of the last candle.
        """
        
        cache_key = LAST_CANDLE_DATE_KEY.format(ticker=self.ticker)
        cached_date = cache.get(cache_key)
        if cached_date is not None:
            return cached_date
        
        first_candle = self.candles.first()
        date = first_candle.time_range.upper if first_candle else None
        cache.set(cache_key, date, timeout=DEFAULT_TIMEOUT)
        return date
    

class BlacklistedStock(models.Model):
    """
    Represents a blacklisted stock.
    """
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name='stock')

    class Meta:
        verbose_name = 'Blacklisted Stock'
        verbose_name_plural = 'Blacklisted Stocks'

    def __str__(self):
        return f'{self.stock.shortname} ({self.stock.ticker})'


class Candle(models.Model):
    """
    Represents a candlestick of historical price data for a stock.
    """

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='candles',
        verbose_name='stock',
        db_index=True,    
    )
    open = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='open',
        help_text='The opening price.',
    )
    close = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='close',
        help_text='The closing price.',
    )
    high = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='high',
        help_text='The highest price.',
    )
    low = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='low',
        help_text='The lowest price.',
    )
    value = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='value',
        help_text='The total value of trades during the candle period.',
    )
    volume = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='volume',
        help_text='The total volume of trades during the candle period.',
    )
    time_range = DateTimeRangeField(
        verbose_name='time range',
        help_text='The time range during which the candlestick represents the trading activity.',
        db_index=True,
    )

    def __str__(self) -> str:
        return f'Candle for {self.stock.shortname}:' \
               f' Open={self.open}, Close={self.close}, High={self.high}, Low={self.low}'

    class Meta:
        verbose_name = 'candle'
        verbose_name_plural = 'candles'
        ordering = ('-time_range',)
        unique_together = ('stock', 'time_range')


class PriceChange(models.Model):
    """
    A model for storing stock price changes.
    """

    stock = models.OneToOneField(
        Stock,
        on_delete=models.CASCADE,
        related_name='price_change',
        verbose_name='stock',
        primary_key=True,
        db_index=True,
    )
    value_per_day = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='value per day')
    percent_per_day = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='percent per day')
    value_per_year = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='value per year')
    percent_per_year = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='percent per year')
    
    updated = models.DateTimeField(auto_now=True, verbose_name='updated')

    def __str__(self):
        return f'{self.stock} - per day: {self.value_per_day}, per year: {self.value_per_year}'
    
    class Meta:
        verbose_name = 'Price Change'
        verbose_name_plural = 'Price Changes'


class Favourite(models.Model):
    """
    A model of the user's favorite stocks.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_stocks', verbose_name='user')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='users', verbose_name='stock')

    class Meta:
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favourites'

    def __str__(self) -> str:
        return f'{self.user.username} - {self.stock.shortname} ({self.stock.ticker})'
