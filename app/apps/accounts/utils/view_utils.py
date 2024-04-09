from functools import wraps

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


def redirect_authenticated_user(url: str):
    """
    A decorator function for redirecting authenticated users.
    
    Parameters:
        - url (str): The URL to which authenticated users are redirected.
    """
    
    def _decorator(view):

        @wraps(view)
        def _wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse_lazy(url))
            return view(request, *args, **kwargs)

        return _wrapper
    
    return _decorator