from django.contrib import admin

from .models import Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    The stock's admin panel.
    """

    list_display = ('ticker', 'shortname', 'prevprice', 'updated')
    search_fields = ('ticker', 'shortname',)
    list_filter = ('status',)
