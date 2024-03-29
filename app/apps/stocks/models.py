from django.db import models


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

    ticker = models.CharField(primary_key=True, max_length=10, verbose_name='ticker', help_text='The ticker of the stock.')
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

    def __str__(self):
        return f'{self.shortname} ({self.ticker}) {self.prevprice} {self.currencyid}'

    class Meta:
        ordering = ('ticker',)
        verbose_name = 'stock'
        verbose_name_plural = 'stocks'

    def save(self, *args, **kwargs):
        if self.ticker:
            self.ticker = self.ticker.upper()
        super().save(*args, **kwargs)
