# auth_app/forms/custom_password_reset_form.py

from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext_lazy as _


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': _('Email Address')
        })
    )