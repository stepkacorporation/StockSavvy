from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Проверяем, существует ли пользователь с таким email
        if sociallogin.is_existing:
            return  # Если профиль уже привязан, ничего не делаем

        email_address = sociallogin.account.extra_data.get('email')
        if not email_address:
            email_address = sociallogin.account.extra_data.get('default_email')

        if not email_address:
            return  # Если email не передан, продолжаем обычную регистрацию

        # Проверяем, есть ли пользователь с таким email
        from allauth.account.models import EmailAddress
        try:
            email = EmailAddress.objects.get(email__iexact=email_address, verified=True)
            # Если email уже существует, связываем социальный аккаунт с этим пользователем
            sociallogin.connect(request, email.user)
        except EmailAddress.DoesNotExist:
            pass

    def on_authentication_error(
            self,
            request,
            provider,
            error=None,
            exception=None,
            extra_context=None,
    ):
        if error == 'cancelled':
            return

        provider_name = provider.name if provider else 'внешний сервис'

        messages.error(request, f'Ошибка входа через {provider_name}. Попробуйте снова')

        raise ImmediateHttpResponse(HttpResponseRedirect(reverse('account_login')))
