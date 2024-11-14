from django.apps import apps
from django.db import models


class StockManager(models.Manager):
    def get_queryset(self):
        BlacklistedStock = apps.get_model('stocks', 'BlacklistedStock')
        return super().get_queryset().exclude(ticker__in=BlacklistedStock.objects.values('stock__ticker'))
