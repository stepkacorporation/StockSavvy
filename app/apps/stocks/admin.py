from django.contrib import admin

from .models import Stock, BlacklistedStock, Candle, PriceChange, Favourite


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Панель администратора для акций.
    """

    list_display = ('ticker', 'shortname', 'prevprice', 'updated')
    search_fields = ('ticker', 'shortname',)
    list_filter = ('status',)


@admin.register(BlacklistedStock)
class BlacklistedStockAdmin(admin.ModelAdmin):
    """
    Панель администратора для акций в черном списке.
    """

    list_display = ('stock_id', 'stock')
    search_fields = ('stock__ticker', 'stock__shortname')
    autocomplete_fields = ('stock',)


@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    """
    Панель администратора для свечей.
    """

    list_display = ('stock', 'open', 'close', 'time_range')
    search_fields = ('stock__ticker',)


@admin.register(PriceChange)
class PriceChangeAdmin(admin.ModelAdmin):
    """
    Панель администратора для изменений цен.
    """

    list_display = ('stock', 'value_per_day', 'value_per_year', 'updated')
    search_fields = ('stock__ticker',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    """
    Панель администратора для избранных акций.
    """

    list_display = ('user', 'stock')
    search_fields = ('user', 'stock')
