from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

api_urlpatterns = [
    path('stocks/', include('apps.stocks.api.urls')),
]

urlpatterns = [
    path('', include('apps.landing.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('stocks/', include('apps.stocks.urls')),

    path('api/', include(api_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
