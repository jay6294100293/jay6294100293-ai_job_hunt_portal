# ai_job_web/auth_app/forms.py

from django import forms

from auth_app.models import CustomUser


class ApiKeyUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['chatgpt_api_key', 'gemini_api_key']

    def clean_chatgpt_api_key(self):
        chatgpt_api_key = self.cleaned_data.get('chatgpt_api_key')
        # Add validation if necessary
        return chatgpt_api_key

    def clean_gemini_api_key(self):
        gemini_api_key = self.cleaned_data.get('gemini_api_key')
        # Add validation if necessary
        return gemini_api_key
