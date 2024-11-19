from django.urls import path

from .views import CandleListAPIView, StockDetailAPIView, AddOrRemoveFavouriteAPIView

urlpatterns = [
    path('favourites/', AddOrRemoveFavouriteAPIView.as_view(), name='api-add-or-remove-favourite'),

    path('<str:ticker>/', StockDetailAPIView.as_view(), name='api-stock-detail'),
    path('<str:ticker>/candles/', CandleListAPIView.as_view(), name='api-candle-list'),
]
