from django.views.generic import ListView, DetailView
from django.db.models import Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import resolve

from .templatetags.formatting_filters import normalize, convert_currency_code
from .utils.view_utils import add_favourite_stocks_to_context, set_no_cache

from .models import Stock


class StockListView(ListView):
    """The view class for displaying the list of stocks."""
    
    model = Stock
    paginate_by = 12
    template_name = 'stocks/stock_list.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        queryset = super().get_queryset()

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

        stock_instance = self.get_object()
        _decimals = stock_instance.decimals
        _currency = convert_currency_code(stock_instance.currencyid)

        opening_price, closing_price = stock_instance.get_opening_and_closing_price_today()
        normalized_last_stock_price = normalize(stock_instance.get_last_price(), places=_decimals)
        
        try:
            value_per_day = stock_instance.price_change.value_per_day
            percent_per_day = normalize(stock_instance.price_change.percent_per_day, places=2, minus=False)
            if value_per_day is not None and percent_per_day is not None:
                _normalized_value_per_day = normalize(value_per_day, places=_decimals, plus=True)
                change_per_day =  f'{_normalized_value_per_day} {_currency} ({percent_per_day}%)'
            else:
                change_per_day = None

            value_per_year = stock_instance.price_change.value_per_year
            percent_per_year = normalize(stock_instance.price_change.percent_per_year, places=2, minus=False)
            if value_per_year is not None and percent_per_year is not None:
                _normalized_value_per_year = normalize(value_per_year, places=_decimals, plus=True)
                change_per_year =  f'{_normalized_value_per_year} {_currency} ({percent_per_year}%)'
            else:
                change_per_year = None
        except ObjectDoesNotExist:
            value_per_day, percent_per_day, change_per_day = None, None, None
            value_per_year, percent_per_year, change_per_year = None, None, None

        
        min_price_per_day, max_price_per_day = stock_instance.get_daily_price_range()
        if min_price_per_day is not None and max_price_per_day is not None:
            min_price_per_day = normalize(min_price_per_day, places=_decimals)
            max_price_per_day = normalize(max_price_per_day, places=_decimals)
            daily_price_range = f'{min_price_per_day} {_currency} - {max_price_per_day} {_currency}'
        else:
            daily_price_range = '-'

        min_price_per_year, max_price_per_year = stock_instance.get_yearly_price_range()
        if min_price_per_year is not None and max_price_per_year is not None:
            min_price_per_year = normalize(min_price_per_year, places=_decimals)
            max_price_per_year = normalize(max_price_per_year, places=_decimals)
            yearly_price_range = f'{min_price_per_year} {_currency} - {max_price_per_year} {_currency}'
        else:
            yearly_price_range = '-'
            
        lot_size = f'1 lot = {stock_instance.lotsize} stocks'

        extra_context = {
            'opening_price': normalize(opening_price, places=_decimals),
            'closing_price': normalize(closing_price, places=_decimals),
            'price_update_date': stock_instance.get_last_candle_date(),
            'last_stock_price': normalized_last_stock_price,
            'value_per_day': value_per_day,
            'change_per_day': change_per_day,
            'value_per_year': value_per_year,
            'change_per_year': change_per_year,
            'daily_price_range': daily_price_range,
            'yearly_price_range': yearly_price_range,
            'lot_size': lot_size,
            'candles': stock_instance.candles,
        }
        
        add_favourite_stocks_to_context(extra_context, self.request.user)

        return context | extra_context
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return set_no_cache(response)
