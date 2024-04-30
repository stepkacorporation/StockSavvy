from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse as HttpResponse
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django_registration.backends.activation.views import RegistrationView
from django.urls import resolve

from .utils.view_utils import redirect_authenticated_user
from .forms import CustomUserCreationForm


class CustomLoginView(LoginView):
    """A custom login view."""

    @method_decorator(redirect_authenticated_user('stocks'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'settings'
        return context
    

class CustomRegistrationView(RegistrationView):
    """A custom view for registering new users."""
    
    form_class = CustomUserCreationForm

    @method_decorator(redirect_authenticated_user('stocks'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'settings'
        return context


@login_required
def settings_view(request):
    current_url_name = resolve(request.path_info).url_name
    return render(request, 'accounts/settings.html', {'current_page': current_url_name})
