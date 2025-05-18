# auth_app/forms/api_update_key_form.py

from django import forms
from auth_app.models import CustomUser


class ApiKeyUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['chatgpt_api_key', 'gemini_api_key']
        widgets = {
            'chatgpt_api_key': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Enter your ChatGPT API Key'
            }),
            'gemini_api_key': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Enter your Gemini API Key'
            }),
        }
        labels = {
            'chatgpt_api_key': 'ChatGPT API Key',
            'gemini_api_key': 'Gemini API Key',
        }
        help_texts = {
            'chatgpt_api_key': 'Your personal API key for accessing ChatGPT services.',
            'gemini_api_key': 'Your personal API key for accessing Gemini services.',
        }

    def clean_chatgpt_api_key(self):
        chatgpt_api_key = self.cleaned_data.get('chatgpt_api_key')
        # Add any specific validation for the ChatGPT API key if necessary
        # Example: if chatgpt_api_key and not chatgpt_api_key.startswith('sk-'):
        #     raise forms.ValidationError('Invalid ChatGPT API key format.')
        return chatgpt_api_key

    def clean_gemini_api_key(self):
        gemini_api_key = self.cleaned_data.get('gemini_api_key')
        # Add any specific validation for the Gemini API key if necessary
        return gemini_api_key

# # ai_job_web/auth_app/forms.py
#
# from django import forms
#
# from auth_app.models import CustomUser
#
#
# class ApiKeyUpdateForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['chatgpt_api_key', 'gemini_api_key']
#
#     def clean_chatgpt_api_key(self):
#         chatgpt_api_key = self.cleaned_data.get('chatgpt_api_key')
#         # Add validation if necessary
#         return chatgpt_api_key
#
#     def clean_gemini_api_key(self):
#         gemini_api_key = self.cleaned_data.get('gemini_api_key')
#         # Add validation if necessary
#         return gemini_api_key
