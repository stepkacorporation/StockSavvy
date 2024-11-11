from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.contrib.auth import get_user_model


class CustomSignupForm(SignupForm):
    class Meta:
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        del self.fields['username']
        del self.fields['password1']
        del self.fields['password2']


class CustomLoginForm(LoginForm):
    class Meta:
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'login' in self.fields:
            self.fields['login'].label = 'Имя пользователя или e-mail'


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(),
        required=False
    )

    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(),
        required=False
    )

    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(),
        required=False,
        help_text=None,
        disabled=True
    )

    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(),
        required=False,
        help_text=None,
        disabled=True
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email')
