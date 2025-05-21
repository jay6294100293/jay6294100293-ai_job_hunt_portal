# auth_app/forms/custom_setPassword_form.py

from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': _('New Password')
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': _('Confirm New Password')
        }),
        strip=False,
    )