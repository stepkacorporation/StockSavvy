from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """
    The user's admin panel.
    """

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'email', 'is_staff')
    list_display_links = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    readonly_fields = ('id',)
    filter_horizontal = ()

    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'username', 'email'),
        }),
        ('Security', {
            'fields': ('password',),
        }),
        ('Other Info', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'last_login', 'created'),
        }),
    )
    add_fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'username', 'email'),
        }),
        ('Security', {
            'fields': ('password1', 'password2'),
        }),
        ('Other Info', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'last_login', 'created'),
        }),
    )
