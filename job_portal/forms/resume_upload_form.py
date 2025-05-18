# job_portal/forms/resume_upload_form.py

from django import forms
from django.core.validators import FileExtensionValidator
# from django.conf import settings # Not strictly needed for this form unless using MAX_UPLOAD_SIZE from settings

# Define MAX_UPLOAD_SIZE here or import from settings if you have it there
MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

class ResumeUploadForm(forms.Form):
    """Form for uploading an existing resume."""
    resume_file = forms.FileField(
        label="Upload your resume",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'odt'])],
        widget=forms.ClearableFileInput( # Using ClearableFileInput for better UX
            attrs={
                # These classes seem to be from DaisyUI or a similar Tailwind component library.
                # Adjust if you're using plain Tailwind or different class names.
                'class': 'file-input file-input-bordered file-input-primary w-full max-w-md text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                'accept': '.pdf,.doc,.docx,.txt,.odt'
            }
        ),
        help_text=f"Supported formats: PDF, DOC, DOCX, TXT, ODT. Max file size: {MAX_UPLOAD_SIZE_MB}MB."
    )

    # The ai_engine field is to let the user choose a preference for parsing,
    # it might not be stored directly in the model but used by your view logic.
    ai_engine = forms.ChoiceField(
        label="Preferred AI Engine for Analysis",
        choices=[
            ('chatgpt', 'ChatGPT (OpenAI)'), # Assuming you might use different models
            ('gemini', 'Google Gemini'),
            # ('default', 'System Default') # Could be an option
        ],
        widget=forms.RadioSelect(
            # attrs={'class': 'radio radio-primary'} # Retaining if this styling is intended
            # For more standard Tailwind, you'd style the label and input pairs.
            # Example for Tailwind (requires more complex template rendering):
            # Each radio button would be styled individually in the template.
        ),
        initial='chatgpt', # Default selection
        help_text="Choose the AI engine you prefer for resume content analysis and enhancement suggestions."
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