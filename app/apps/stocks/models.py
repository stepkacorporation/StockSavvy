from datetime import timedelta, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import DateTimeRangeField
from django.core.cache import cache
from django.db import models
from django.db.models import Min, Max
from django.urls import reverse
from django.utils import timezone

from .managers import StockManager
from .utils.cache_keys import (
    DEFAULT_TIMEOUT,
    LAST_PRICE_KEY,
    LAST_CANDLE_DATE_KEY,
    OPENING_CLOSING_PRICE_TODAY_KEY,
)

User = get_user_model()


class Stock(models.Model):
    """Акция"""

    ticker = models.CharField(
        primary_key=True,
        max_length=10,
        verbose_name='тикер',
        help_text='Тикер акции.',
        db_index=True,
    )
    shortname = models.CharField(
        max_length=50,
        verbose_name='краткое название',
        help_text='Краткое название инструмента.',
        null=True,
    )
    secname = models.CharField(
        max_length=50,
        verbose_name='название',
        help_text='Название финансового инструмента.',
        null=True,
    )
    latname = models.CharField(
        max_length=50,
        verbose_name='латинское название',
        help_text='Название финансового инструмента на английском языке.',
        null=True,
    )
    prevprice = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=10,
        verbose_name='предыдущая цена',
        help_text='Цена последней сделки предыдущего дня.',
        null=True,
    )
    lotsize = models.PositiveIntegerField(
        verbose_name='размер лота',
        help_text='Количество ценных бумаг в одном стандартном лоте.',
        null=True,
    )
    facevalue = models.DecimalField(
        max_digits=34,
        decimal_places=17,
        verbose_name='номинальная стоимость',
        help_text='Номинальная стоимость одной ценной бумаги на текущую дату.',
        null=True,
    )
    faceunit = models.CharField(
        max_length=10,
        verbose_name='валюта номинала',
        help_text='Код валюты, в которой выражена номинальная стоимость ценной бумаги.',
        null=True,
    )
    status = models.CharField(
        max_length=1,
        verbose_name='статус',
        help_text='Индикатор "разрешены/запрещены торговые операции".',
        null=True,
    )
    decimals = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='количество десятичных знаков',
        help_text='Количество десятичных знаков дробной части числа. Используется для '
                  'форматирования значений полей с типом DECIMAL.',
        null=True,
    )
    minstep = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        verbose_name='минимальный шаг',
        help_text='Минимально возможная разница между ценами, указанными в заявках на '
                  'покупку/продажу ценных бумаг.',
        null=True,
    )
    prevdate = models.DateField(
        verbose_name='дата предыдущей торговой сессии',
        help_text='Дата предыдущего торгового дня.',
        null=True,
    )
    issuesize = models.PositiveBigIntegerField(
        verbose_name='объем выпуска',
        help_text='Количество ценных бумаг в выпуске.',
        null=True,
    )
    isin = models.CharField(
        max_length=20,
        verbose_name='ISIN',
        help_text='Международный идентификационный код ценной бумаги.',
        null=True,
    )
    regnumber = models.CharField(
        max_length=50,
        verbose_name='регистрационный номер',
        help_text='Номер государственной регистрации.',
        null=True,
    )
    prevlegalcloseprice = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=10,
        verbose_name='официальная цена закрытия',
        help_text="Официальная цена закрытия предыдущего дня, рассчитанная по правилам торговли "
                  "как средневзвешенная цена сделок за последние 10 минут основной сессии, включая "
                  "сделки в постторговый период или на аукционе закрытия.",
        null=True,
    )
    currencyid = models.CharField(
        max_length=10,
        verbose_name='валюта',
        help_text='Валюта расчетов по инструменту.',
        null=True,
    )
    sectype = models.CharField(
        max_length=1,
        verbose_name='тип ценной бумаги',
        help_text='Тип ценной бумаги.',
        null=True,
    )
    listlevel = models.PositiveSmallIntegerField(
        verbose_name='уровень листинга',
        help_text='Уровень листинга.',
        null=True,
    )
    settledate = models.DateField(
        verbose_name='дата расчетов',
        help_text='Дата расчетов по сделке.',
        null=True,
    )

    updated = models.DateTimeField(auto_now=True, verbose_name='обновлено')

    objects = StockManager()

    def __str__(self) -> str:
        return f'{self.shortname} ({self.ticker}) {self.prevprice} {self.currencyid}'

    class Meta:
        verbose_name = 'акция'
        verbose_name_plural = 'акции'
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
            time_range__overlap=[start_of_day, end_of_day + timedelta(days=1)]
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
    Представляет акцию в черном списке.
    """

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name='акция')

    class Meta:
        verbose_name = 'Акция в черном списке'
        verbose_name_plural = 'Акции в черном списке'

    def __str__(self):
        return f'{self.stock.shortname} ({self.stock.ticker})'


class Candle(models.Model):
    """
    Представляет свечу исторических данных о цене акции.
    """

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='candles',
        verbose_name='акция',
        db_index=True,
    )
    open = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='открытие',
        help_text='Цена открытия.',
    )
    close = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='закрытие',
        help_text='Цена закрытия.',
    )
    high = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='максимум',
        help_text='Самая высокая цена.',
    )
    low = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='минимум',
        help_text='Самая низкая цена.',
    )
    value = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='стоимость',
        help_text='Общая стоимость сделок за период свечи.',
    )
    volume = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        verbose_name='объем',
        help_text='Общий объем сделок за период свечи.',
    )
    time_range = DateTimeRangeField(
        verbose_name='временной диапазон',
        help_text='Временной диапазон, в течение которого свеча представляет торговую активность.',
        db_index=True,
    )

    def __str__(self) -> str:
        return f'Свеча для {self.stock.shortname}: Открытие={self.open}, Закрытие={self.close}, Максимум={self.high}, Минимум={self.low}'

    class Meta:
        verbose_name = 'свеча'
        verbose_name_plural = 'свечи'
        ordering = ('-time_range',)
        unique_together = ('stock', 'time_range')


class PriceChange(models.Model):
    """
    Модель для хранения изменений цены акции.
    """

    stock = models.OneToOneField(
        Stock,
        on_delete=models.CASCADE,
        related_name='price_change',
        verbose_name='акция',
        primary_key=True,
        db_index=True,
    )
    value_per_day = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='изменение в день')
    percent_per_day = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='процент в день')
    value_per_year = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='изменение в год')
    percent_per_year = models.DecimalField(max_digits=36, decimal_places=18, verbose_name='процент в год')

    updated = models.DateTimeField(auto_now=True, verbose_name='обновлено')

    def __str__(self):
        return f'{self.stock} - за день: {self.value_per_day}, за год: {self.value_per_year}'

    class Meta:
        verbose_name = 'Изменение цены'
        verbose_name_plural = 'Изменения цены'


class Favourite(models.Model):
    """
    Модель избранных акций пользователя.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_stocks',
                             verbose_name='пользователь')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='users', verbose_name='акция')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self) -> str:
        return f'{self.user.username} - {self.stock.shortname} ({self.stock.ticker})'
