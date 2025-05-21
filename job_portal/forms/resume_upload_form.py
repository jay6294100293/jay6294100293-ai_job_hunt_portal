# job_portal/forms/resume_upload_form.py

from django import forms
from django.core.validators import FileExtensionValidator

# Define MAX_UPLOAD_SIZE here or import from settings if you have it there
MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


class ResumeUploadForm(forms.Form):
    """Form for uploading an existing resume."""
    resume_file = forms.FileField(
        label="Upload your resume",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'odt'])],
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'file-input file-input-bordered file-input-primary w-full max-w-md text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                'accept': '.pdf,.doc,.docx,.txt,.odt'
            }
        ),
        help_text=f"Supported formats: PDF, DOC, DOCX, TXT, ODT. Max file size: {MAX_UPLOAD_SIZE_MB}MB."
    )

    # The ai_engine field is to let the user choose a preference for parsing
    ai_engine = forms.ChoiceField(
        label="Preferred AI Engine for Analysis",
        choices=[
            ('chatgpt', 'ChatGPT (OpenAI)'),
            ('gemini', 'Google Gemini'),
        ],
        widget=forms.RadioSelect(),
        initial='chatgpt',
        help_text="Choose the AI engine you prefer for resume content analysis and enhancement suggestions."
    )

    # Option to enable/disable AI parsing
    ai_parsing_enabled = forms.BooleanField(
        label="Use AI for enhanced resume parsing",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded'}),
        help_text="Uncheck if you prefer basic parsing without AI assistance."
    )

    def clean_resume_file(self):
        resume_file = self.cleaned_data.get('resume_file')
        if resume_file:
            if resume_file.size > MAX_UPLOAD_SIZE_BYTES:
                raise forms.ValidationError(f"File size must be no more than {MAX_UPLOAD_SIZE_MB}MB.")
        return resume_file

# # job_portal/forms/resume_upload_form.py
#
# from django import forms
# from django.core.validators import FileExtensionValidator
#
#
# class ResumeUploadForm(forms.Form):
#     """Form for uploading an existing resume."""
#     resume_file = forms.FileField(
#         validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'odt'])],
#         widget=forms.FileInput(
#             attrs={
#                 'class': 'file-input file-input-bordered w-full max-w-xs',
#                 'accept': '.pdf,.doc,.docx,.txt,.odt'
#             }
#         ),
#         help_text="Upload your resume in PDF, Word, or text format."
#     )
#
#     ai_engine = forms.ChoiceField(
#         choices=[
#             ('chatgpt', 'ChatGPT (GPT-3.5)'),
#             ('gemini', 'Google Gemini')
#         ],
#         widget=forms.RadioSelect(
#             attrs={'class': 'radio radio-primary'}
#         ),
#         initial='chatgpt',
#         help_text="Choose the AI engine to analyze your resume"
#     )
#
#     def clean_resume_file(self):
#         resume_file = self.cleaned_data.get('resume_file')
#         # Limit the file size to 5MB
#         if resume_file and resume_file.size > 5 * 1024 * 1024:  # 5MB
#             raise forms.ValidationError("File size must be under 5MB.")
#         return resume_file