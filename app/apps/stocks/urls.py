from django.urls import path

from .views import StockListView, StockDetailView

urlpatterns = [
    path('', StockListView.as_view(), name='stocks'),
    path('<slug:ticker>/', StockDetailView.as_view(), name='stock-detail'),
]