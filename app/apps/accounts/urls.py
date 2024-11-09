from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.CustomSignupView.as_view(), name='account_signup'),
    path('login/', views.CustomLoginView.as_view(), name='account_login'),
    path('settings/', views.SettingsView.as_view(), name='account_settings'),

    path('3rdparty/login/cancelled/', views.CustomLoginCanceledView.as_view(), name='socialaccount_login_cancelled'),
    path('3rdparty/login/error/', views.CustomLoginErrorView.as_view(), name='socialaccount_login_error'),
]

unused_routes = [
    'email/',
    'confirm-email/',
    'confirm-email/<str:key>/',

    'password/change/',
    'password/set/',

    'social/connections/',
    '3rdparty/',
]

for route in unused_routes:
    urlpatterns.append(path(route, views.raise_404))
