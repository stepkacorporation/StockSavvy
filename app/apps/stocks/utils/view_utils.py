from django.template.response import TemplateResponse

from apps.accounts.models import User

from ..models import Favourite


def add_favourite_stocks_to_context(context: dict, user: User) -> dict:
    """
    Adds the user's favourite stocks to the context dictionary if the user is authenticated.

    Parameters:
    - context (dict): A dictionary representing the context of the request.
    - user (User): The user object for whom to retrieve favourite stocks.

    Returns:
    - dict: The context dictionary with the 'favourite_stocks' key containing the user's favourite stock tickers.
    """

    if user.is_authenticated:
        favourite_stocks = Favourite.objects.filter(user=user).values_list('stock__ticker', flat=True)
        context['favourite_stocks'] = favourite_stocks
    
    return context


def set_no_cache(response: TemplateResponse) -> TemplateResponse:
    """
    Sets the Cache-Control, Pragma, and Expires headers in the response to disable caching.

    Args:
    - response (TemplateResponse): TemplateResponse object to modify.

    Returns:
    - TemplateResponse: Modified TemplateResponse object with caching disabled.
    """

    response["Cache-Control"] = "no-cache, no-store, must-revalidate"  # HTTP 1.1.
    response["Pragma"] = "no-cache"  # HTTP 1.0.
    response["Expires"] = "0"  # Proxies.
    return response
