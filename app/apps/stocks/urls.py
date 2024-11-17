from django.urls import path

from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='stocks'),
    path('favourites/', views.FavouriteStockListView.as_view(), name='favourite-stocks'),
    path('<slug:ticker>/', views.StockDetailView.as_view(), name='stock-detail'),
]
