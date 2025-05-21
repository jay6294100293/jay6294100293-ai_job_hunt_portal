# auth_app/forms/profile_update_form.py

from django import forms
from django.utils.translation import gettext_lazy as _
from auth_app.models import CustomUser


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'profile_picture', 'default_address', 'default_linkedin_url',
            'default_github_url', 'default_portfolio_url', 'default_summary'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': _('e.g., +1 (555) 123-4567')
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
            }),
            'default_address': forms.Textarea(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'rows': 3,
                'placeholder': _('Your address')
            }),
            'default_linkedin_url': forms.URLInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': _('https://www.linkedin.com/in/your-profile')
            }),
            'default_github_url': forms.URLInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': _('https://github.com/your-username')
            }),
            'default_portfolio_url': forms.URLInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': _('https://your-portfolio.com')
            }),
            'default_summary': forms.Textarea(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'rows': 5,
                'placeholder': _('A brief summary of your professional background and skills...')
            }),
        }
        labels = {
            'phone_number': _('Phone Number'),
            'profile_picture': _('Profile Picture'),
            'default_address': _('Address'),
            'default_linkedin_url': _('LinkedIn Profile'),
            'default_github_url': _('GitHub Profile'),
            'default_portfolio_url': _('Portfolio Website'),
            'default_summary': _('Professional Summary'),
        }
        help_texts = {
            'default_linkedin_url': _('Full URL to your LinkedIn profile.'),
            'default_github_url': _('Full URL to your GitHub profile.'),
            'default_portfolio_url': _('Full URL to your personal website or portfolio.'),
            'default_summary': _('A concise overview of your professional background, skills, and career objectives.'),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id

        # Check if email already exists for a different user
        if email and CustomUser.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError(_("This email is already in use by another account."))
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Add phone number validation logic if needed
        return phone

    def clean_default_linkedin_url(self):
        url = self.cleaned_data.get('default_linkedin_url')
        if url and not (url.startswith('https://www.linkedin.com/') or url.startswith('http://www.linkedin.com/')):
            raise forms.ValidationError(_("Please enter a valid LinkedIn URL."))
        return url

    def clean_default_github_url(self):
        url = self.cleaned_data.get('default_github_url')
        if url and not (url.startswith('https://github.com/') or url.startswith('http://github.com/')):
            raise forms.ValidationError(_("Please enter a valid GitHub URL."))
        return url