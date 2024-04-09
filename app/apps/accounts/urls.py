from django.urls import path, include

from .views import CustomLoginView, CustomRegistrationView, settings_view

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegistrationView.as_view(), name='django_registration_register'),
    path('', include('django_registration.backends.activation.urls')),
    path('', include('django.contrib.auth.urls')),
    path('settings/', settings_view, name='settings'),
]