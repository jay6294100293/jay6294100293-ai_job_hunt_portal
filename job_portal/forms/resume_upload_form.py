# job_portal/forms/resume_upload_form.py

from django import forms
from django.core.validators import FileExtensionValidator


class ResumeUploadForm(forms.Form):
    """Form for uploading an existing resume."""
    resume_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'odt'])],
        widget=forms.FileInput(
            attrs={
                'class': 'file-input file-input-bordered w-full max-w-xs',
                'accept': '.pdf,.doc,.docx,.txt,.odt'
            }
        ),
        help_text="Upload your resume in PDF, Word, or text format."
    )

    ai_engine = forms.ChoiceField(
        choices=[
            ('chatgpt', 'ChatGPT (GPT-3.5)'),
            ('gemini', 'Google Gemini')
        ],
        widget=forms.RadioSelect(
            attrs={'class': 'radio radio-primary'}
        ),
        initial='chatgpt',
        help_text="Choose the AI engine to analyze your resume"
    )

    def clean_resume_file(self):
        resume_file = self.cleaned_data.get('resume_file')
        # Limit the file size to 5MB
        if resume_file and resume_file.size > 5 * 1024 * 1024:  # 5MB
            raise forms.ValidationError("File size must be under 5MB.")
        return resume_file