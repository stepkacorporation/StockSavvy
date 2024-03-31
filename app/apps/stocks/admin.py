from django.contrib import admin

from .models import Stock, Candle


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    The stock's admin panel.
    """

    list_display = ('ticker', 'shortname', 'prevprice', 'updated')
    search_fields = ('ticker', 'shortname',)
    list_filter = ('status',)


@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    """
    The candle's admin panel.
    """

    list_display = ('stock', 'open', 'close', 'time_range')
    search_fields = ('stock__ticker',)
