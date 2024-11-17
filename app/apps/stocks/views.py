from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.urls import resolve
from django.views.generic import ListView, DetailView

from .models import Stock
from .templatetags.formatting_filters import normalize, convert_currency_code
from .utils.cache_keys import DEFAULT_TIMEOUT, STOCK_DETAIL_KEY
from .utils.views import add_favourite_stocks_to_context, set_no_cache, get_price_info, get_price_range


class StockListView(ListView):
    """The view class for displaying the list of stocks."""

    model = Stock
    paginate_by = 12
    template_name = 'stocks/stock_list.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('price_change')

        query = self.request.GET.get('query')
        sort_by = self.request.GET.get('sort_by')
        order = '-' if self.request.GET.get('order', 'asc') == 'desc' else ''

        if query:
            queryset = queryset.filter(
                Q(ticker__icontains=query) |
                Q(shortname__icontains=query) |
                Q(secname__icontains=query) |
                Q(latname__icontains=query)
            )

        if sort_by == 'name':
            queryset = queryset.order_by(f'{order}short{sort_by}', 'ticker')
        elif sort_by == 'price':
            queryset = queryset.annotate(
                prevprice_default=Coalesce('prevprice', Value(0), output_field=DecimalField())
            ).order_by(f'{order}prevprice_default', 'shortname')
        elif sort_by == 'per_day':
            queryset = queryset.annotate(
                percent_per_day_default=Coalesce('price_change__percent_per_day', Value(0), output_field=DecimalField())
            ).order_by(f'{order}percent_per_day_default', 'shortname')
        elif sort_by == 'per_year':
            queryset = queryset.annotate(
                percent_per_year_default=Coalesce(
                    'price_change__percent_per_year', Value(0), output_field=DecimalField()
                )
            ).order_by(f'{order}percent_per_year_default', 'shortname')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        params = self.request.GET.copy()

        params.pop('page', None)
        params.pop('sort_by', None)
        params.pop('order', None)

        context['params'] = params.urlencode()

        add_favourite_stocks_to_context(context, self.request.user)

        current_url_name = resolve(self.request.path_info).url_name
        context['current_page'] = current_url_name

        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return set_no_cache(response)


class FavouriteStockListView(LoginRequiredMixin, StockListView):
    """
    View class for displaying the list of favorite stocks for authenticated users only.
    """

    paginate_by = None
    template_name = 'stocks/favourite_stock_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(users__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_on_delete'] = True
        return context


class StockDetailView(DetailView):
    """The view class for displaying the details of the stock."""

    model = Stock
    template_name = 'stocks/stock_detail.html'
    context_object_name = 'stock'
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stock: Stock = context['stock']
        _decimals = stock.decimals
        _currency = convert_currency_code(stock.currencyid)

        cache_key = STOCK_DETAIL_KEY.format(ticker=stock.ticker)
        cached_context = cache.get(cache_key)
        if cached_context:
            add_favourite_stocks_to_context(context, self.request.user)
            return context | cached_context

        opening_price, closing_price = stock.get_opening_and_closing_price_today()
        normalized_last_stock_price = normalize(stock.get_last_price(), places=_decimals)

        value_per_day, _, change_per_day = get_price_info(stock, decimals=_decimals, currency=_currency, per='day')
        value_per_year, _, change_per_year = get_price_info(stock, decimals=_decimals, currency=_currency, per='year')

        daily_price_range = get_price_range(stock, _decimals, _currency, per='day')
        yearly_price_range = get_price_range(stock, _decimals, _currency, per='year')

        lot_size = f'1 lot = {stock.lotsize} stocks'

        extra_context = {
            'opening_price': normalize(opening_price, places=_decimals),
            'closing_price': normalize(closing_price, places=_decimals),
            'price_update_date': stock.get_last_candle_date(),
            'last_stock_price': normalized_last_stock_price,
            'value_per_day': value_per_day,
            'change_per_day': change_per_day,
            'value_per_year': value_per_year,
            'change_per_year': change_per_year,
            'daily_price_range': daily_price_range,
            'yearly_price_range': yearly_price_range,
            'lot_size': lot_size,
        }

        cache.set(cache_key, extra_context, timeout=DEFAULT_TIMEOUT)

        add_favourite_stocks_to_context(context, self.request.user)

        return context | extra_context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return set_no_cache(response)
