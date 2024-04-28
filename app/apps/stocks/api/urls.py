from django.urls import path

from .views import CandleListAPIView, StockDetailAPIView

urlpatterns = [
    path('<str:ticker>/', StockDetailAPIView.as_view(), name='api-stock-detail'),
    path('<str:ticker>/candles/', CandleListAPIView.as_view(), name='api-candle-list'),
]
