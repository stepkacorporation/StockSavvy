from django.urls import path

from .views import StockListView, FavouriteStockListView, StockDetailView

urlpatterns = [
    path('', StockListView.as_view(), name='stocks'),
    path('favourites/', FavouriteStockListView.as_view(), name='favourite-stocks'),
    path('<slug:ticker>/', StockDetailView.as_view(), name='stock-detail'),
]