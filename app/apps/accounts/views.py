from allauth.account.forms import ChangePasswordForm, SetPasswordForm
from allauth.account.internal.decorators import login_not_required
from allauth.account.views import SignupView, LoginView
from allauth.socialaccount.views import LoginCancelledView, LoginErrorView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, Http404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views.generic import TemplateView

from .forms import UserProfileForm


def raise_404(request, *args, **kwargs):
    raise Http404


class CustomSignupView(SignupView):
    def form_valid(self, form):
        user, resp = form.try_save(self.request)

        if resp:
            return resp

        password = get_random_string(14)
        user.set_password(password)
        user.save()

        # Отправка HTML-письма с информацией для входа
        subject = 'Регистрация на StockSavvy'

        # Рендерим HTML-шаблон письма
        html_message = render_to_string('account/email/registration_email.html', {
            'username': user.username,
            'email': user.email,
            'password': password,
        })
        plain_message = strip_tags(html_message)  # Создание текстовой версии письма

        send_mail(
            subject,
            plain_message,  # Текстовая версия
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,  # HTML-версия
            fail_silently=False,
        )

        messages.success(self.request, f'На вашу почту было отправлено письмо с данными для входа в аккаунт')

        return HttpResponseRedirect(reverse('account_login'))


class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)

        user = form.user

        if user and not user.emailaddress_set.filter(verified=True).exists():
            # Подтверждаем email
            user.emailaddress_set.update(verified=True)

        return response


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'account/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['profile_form'] = UserProfileForm(instance=user)

        context['password_form'] = ChangePasswordForm(user) if user.has_usable_password() else None
        context['set_password_form'] = SetPasswordForm(user) if not user.has_usable_password() else None

        return context

    def post(self, request, *args, **kwargs):
        user = request.user

        if 'profile_form' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Личные данные сохранены')
        else:
            profile_form = UserProfileForm(instance=user)

        if 'password_form' in request.POST and user.has_usable_password():
            password_form = ChangePasswordForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
                messages.success(request, 'Пароль успешно изменён')
        else:
            password_form = ChangePasswordForm(user)

        if 'set_password_form' in request.POST and not user.has_usable_password():
            set_password_form = SetPasswordForm(user, request.POST)
            if set_password_form.is_valid():
                set_password_form.save()
                login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
                messages.success(request, 'Пароль успешно установлен')
        else:
            set_password_form = SetPasswordForm(user)

        return self.render_to_response({
            'profile_form': profile_form,
            'password_form': password_form if user.has_usable_password() else None,
            'set_password_form': set_password_form if not user.has_usable_password() else None
        })


@method_decorator(login_not_required, name='dispatch')
class CustomLoginCanceledView(LoginCancelledView):
    def get(self, request, *args, **kwargs):
        messages.error(request, 'Вы прервали авторизацию. Пожалуйста, попробуйте еще раз')
        return HttpResponseRedirect(reverse('account_login'))


class CustomLoginErrorView(LoginErrorView):
    def get(self, request, *args, **kwargs):
        messages.error(request, 'При попытке войти через учетную запись стороннего сервиса произошла ошибка')
        return HttpResponseRedirect(reverse('account_login'))
