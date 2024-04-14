from django.views.generic import ListView, DetailView
from django.db.models import Q, Value, DecimalField
from django.db.models.functions import Coalesce

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
            queryset = queryset.order_by(f'{order}price_change__percent_per_day', 'shortname')
        elif sort_by == 'per_year':
            queryset = queryset.order_by(f'{order}price_change__percent_per_year', 'shortname')

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        params = self.request.GET.copy()

        params.pop('page', None)
        params.pop('sort_by', None)
        params.pop('order', None)

        context['params'] = params.urlencode()
        return context


class StockDetailView(DetailView):
    """The view class for displaying the details of the stock."""

    model = Stock
    template_name = 'stocks/stock_detail.html'
    context_object_name = 'stock'
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'