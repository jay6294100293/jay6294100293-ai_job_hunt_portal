# job_portal/forms/resume_creation_form.py

from django import forms
from django.forms import inlineformset_factory

from ..models import (
    Resume, Skill, Experience, ExperienceBulletPoint,
    Education, Certification, Project, ProjectBulletPoint,
    Language, CustomData # Ensuring CustomData matches your model name
)

# Tailwind CSS classes for form inputs (reusable)
tailwind_input_classes = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
tailwind_textarea_classes = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm h-24'
tailwind_checkbox_classes = 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
tailwind_date_classes = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
tailwind_file_input_classes = 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
tailwind_select_classes = 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md'


class ResumeMetaForm(forms.ModelForm):
    """Form for Resume metadata like title and template."""
    class Meta:
        model = Resume
        fields = ['title', 'template_name']
        widgets = {
            'title': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'e.g., Software Engineer Resume'}),
            'template_name': forms.Select(attrs={'class': tailwind_select_classes}), # Assuming you'll populate choices
        }

class ResumeBasicInfoForm(forms.ModelForm):
    """Form for the personal information section of the resume (fields on Resume model)."""
    class Meta:
        model = Resume
        fields = [
            'first_name', 'mid_name', 'last_name', 'email',
            'phone', 'address', 'linkedin', 'github', 'portfolio',
            'profile_picture' # Added profile_picture
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'First Name'}),
            'mid_name': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Middle Name (Optional)'}),
            'last_name': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': tailwind_input_classes, 'placeholder': 'your.email@example.com'}),
            'phone': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': '+1 (555) 123-4567'}),
            'address': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 3, 'placeholder': '123 Main St, City, State, Zip Code, Country'}),
            'linkedin': forms.URLInput(attrs={'class': tailwind_input_classes, 'placeholder': 'linkedin.com/in/yourprofile'}),
            'github': forms.URLInput(attrs={'class': tailwind_input_classes, 'placeholder': 'github.com/yourusername'}),
            'portfolio': forms.URLInput(attrs={'class': tailwind_input_classes, 'placeholder': 'yourportfolio.com'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': tailwind_file_input_classes}),
        }

class ResumeSummaryForm(forms.ModelForm):
    """Form for the resume summary section."""
    class Meta:
        model = Resume
        fields = ['summary']
        widgets = {
            'summary': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 5, 'placeholder': 'Write a brief professional summary detailing your key skills and career goals...'}),
        }

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'city', 'state', 'country', 'is_current', 'description']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Job Title'}),
            'company': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Company Name'}),
            'city': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Country'}),
            'start_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': tailwind_checkbox_classes + ' mr-2'}),
            'description': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 4, 'placeholder': 'Briefly describe your overall role and responsibilities.'}),
        }

class ExperienceBulletPointForm(forms.ModelForm):
    class Meta:
        model = ExperienceBulletPoint
        fields = ['bullet_point']
        widgets = {
            'bullet_point': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 2, 'placeholder': 'Key achievement or responsibility (e.g., Led a team of 5 engineers...)'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'city', 'state', 'country', 'gpa', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Institution Name'}),
            'degree': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Degree (e.g., Bachelor of Science)'}),
            'field_of_study': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Field of Study (e.g., Computer Science)'}),
            'city': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Country'}),
            'start_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date'}),
            'gpa': forms.NumberInput(attrs={'class': tailwind_input_classes, 'placeholder': 'GPA (e.g., 3.8/4.0)'}),
            'description': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 3, 'placeholder': 'Optional: Relevant coursework, honors, thesis, or academic achievements.'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'proficiency', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Skill Name (e.g., Python)'}),
            'proficiency': forms.Select(attrs={'class': tailwind_select_classes}),
            'category': forms.Select(attrs={'class': tailwind_select_classes}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'url', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Project Title'}),
            'description': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 4, 'placeholder': 'Describe the project, your role, and technologies used.'}),
            'url': forms.URLInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Link to project (GitHub, live demo)'}),
            'start_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date'}),
        }

class ProjectBulletPointForm(forms.ModelForm):
    class Meta:
        model = ProjectBulletPoint
        fields = ['bullet_point']
        widgets = {
            'bullet_point': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 2, 'placeholder': 'Key feature or contribution (e.g., Implemented user authentication...)'}),
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'expiration_date', 'credential_id', 'credential_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Certification Name'}),
            'issuing_organization': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Issuing Organization'}),
            'issue_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': tailwind_date_classes, 'type': 'date', 'placeholder': 'Optional'}),
            'credential_id': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Credential ID (Optional)'}),
            'credential_url': forms.URLInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Credential URL (Optional)'}),
        }

class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name', 'proficiency']
        widgets = {
            'name': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Language (e.g., English, Spanish)'}),
            'proficiency': forms.Select(attrs={'class': tailwind_select_classes}),
        }

class CustomDataForm(forms.ModelForm):
    class Meta:
        model = CustomData
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': tailwind_input_classes, 'placeholder': 'Custom Section Title (e.g., Awards and Honors)'}),
            'description': forms.Textarea(attrs={'class': tailwind_textarea_classes, 'rows': 4, 'placeholder': 'Details for this custom section.'}),
        }


# Formsets for related models, using inlineformset_factory
# These allow adding multiple entries for experiences, skills, etc., for a single resume.

ExperienceBulletPointInlineFormSet = inlineformset_factory(
    Experience, ExperienceBulletPoint, form=ExperienceBulletPointForm,
    fields=['bullet_point'], extra=1, can_delete=True
)

ProjectBulletPointInlineFormSet = inlineformset_factory(
    Project, ProjectBulletPoint, form=ProjectBulletPointForm,
    fields=['bullet_point'], extra=1, can_delete=True
)

# Formsets for sections directly related to the Resume model
ExperienceInlineFormSet = inlineformset_factory(
    Resume, Experience, form=ExperienceForm,
    extra=1, can_delete=True, fk_name='resume'
)

EducationInlineFormSet = inlineformset_factory(
    Resume, Education, form=EducationForm,
    extra=1, can_delete=True, fk_name='resume'
)

SkillInlineFormSet = inlineformset_factory(
    Resume, Skill, form=SkillForm,
    extra=3, can_delete=True, fk_name='resume' # Allow adding a few skills at once
)

ProjectInlineFormSet = inlineformset_factory(
    Resume, Project, form=ProjectForm,
    extra=1, can_delete=True, fk_name='resume'
)

CertificationInlineFormSet = inlineformset_factory(
    Resume, Certification, form=CertificationForm,
    extra=1, can_delete=True, fk_name='resume'
)

LanguageInlineFormSet = inlineformset_factory(
    Resume, Language, form=LanguageForm,
    extra=1, can_delete=True, fk_name='resume'
)

CustomDataInlineFormSet = inlineformset_factory(
    Resume, CustomData, form=CustomDataForm,
    extra=1, can_delete=True, fk_name='resume'
)

# # resumes/forms.py
#
# from django import forms
# from django.forms import inlineformset_factory, modelformset_factory
# from django.shortcuts import render
#
# # It's better practice to define models in models.py, not import from ..models here
# # Assuming these models are correctly defined elsewhere
# from ..models import (
#     Resume, Skill, Experience, ExperienceBulletPoint,
#     Education, Certification, Project, ProjectBulletPoint,
#     Language, CustomData
# )
#
# from django import forms
# from django.core.validators import FileExtensionValidator
# from django.conf import settings
#
#
# class ResumeBasicInfoForm(forms.ModelForm):
#     """Form for the basic personal information of the resume."""
#
#     class Meta:
#         model = Resume
#         fields = [
#             'first_name', 'mid_name', 'last_name', 'email',
#             'phone', 'address', 'linkedin', 'github', 'portfolio'
#         ]
#         # Removed 'class' attributes from widgets
#         widgets = {
#             'first_name': forms.TextInput(),
#             'mid_name': forms.TextInput(),
#             'last_name': forms.TextInput(),
#             'email': forms.EmailInput(),
#             'phone': forms.TextInput(),
#             'address': forms.Textarea(attrs={'rows': 3}),
#             'linkedin': forms.URLInput(),
#             'github': forms.URLInput(),
#             'portfolio': forms.URLInput(),
#         }
#
#
# class ResumeSummaryForm(forms.ModelForm):
#     """Form for the professional summary of the resume."""
#
#     class Meta:
#         model = Resume
#         fields = ['summary']
#         # Removed 'class' attributes from widgets
#         widgets = {
#             'summary': forms.Textarea(
#                 attrs={
#                     'rows': 5,
#                     'placeholder': 'Write a professional summary of your skills and experience (100 characters minimum)'
#                 }
#             ),
#         }
#
#
# class SkillForm(forms.ModelForm):
#     """Form for individual skill entries."""
#
#     class Meta:
#         model = Skill
#         fields = ['skill_name', 'skill_type', 'proficiency_level']
#          # Removed 'class' attributes from widgets, kept functional attrs
#         widgets = {
#             'skill_name': forms.TextInput(),
#             'skill_type': forms.Select(),
#             'proficiency_level': forms.NumberInput(
#                 attrs={
#                     # Note: 'range' class was likely for DaisyUI styling, removing it.
#                     # You'll need to style this range input with Tailwind in the template.
#                     'min': '0',
#                     'max': '100',
#                     'step': '10',
#                     # Keep JS interaction if needed, but styling is now template's job
#                     'oninput': 'this.nextElementSibling.value = this.value'
#                 }
#             ),
#         }
#
#
# class ExperienceForm(forms.ModelForm):
#     """Form for work experience entries."""
#
#     class Meta:
#         model = Experience
#         fields = [
#             'job_title', 'employer', 'location',
#             'start_date', 'end_date', 'is_current'
#         ]
#          # Removed 'class' attributes from widgets, kept functional attrs
#         widgets = {
#             'job_title': forms.TextInput(),
#             'employer': forms.TextInput(),
#             'location': forms.TextInput(),
#             'start_date': forms.DateInput(
#                 attrs={'type': 'date'} # Kept type attribute
#             ),
#             'end_date': forms.DateInput(
#                 attrs={'type': 'date'} # Kept type attribute
#             ),
#             'is_current': forms.CheckboxInput(
#                 # Note: 'checkbox' class was likely for DaisyUI styling, removing it.
#                 # Apply Tailwind classes for checkboxes in the template.
#                 attrs={'onchange': 'toggleEndDate(this)'} # Kept functional JS
#             ),
#         }
#
#
# class ExperienceBulletPointForm(forms.ModelForm):
#     """Form for experience bullet points."""
#     # Note: This form/formset might not be used based on previous analysis
#
#     class Meta:
#         model = ExperienceBulletPoint
#         fields = ['description']
#         # Removed 'class' attributes from widgets
#         widgets = {
#             'description': forms.Textarea(
#                 attrs={'rows': 2}
#             ),
#         }
#
#
# class EducationForm(forms.ModelForm):
#     """Form for education entries."""
#
#     class Meta:
#         model = Education
#         fields = [
#             'school_name', 'location', 'degree',
#             'degree_type', 'field_of_study',
#             'graduation_date', 'gpa'
#         ]
#          # Removed 'class' attributes from widgets, kept functional attrs
#         widgets = {
#             'school_name': forms.TextInput(),
#             'location': forms.TextInput(),
#             'degree': forms.TextInput(),
#             'degree_type': forms.Select(),
#             'field_of_study': forms.TextInput(),
#             'graduation_date': forms.DateInput(
#                 attrs={'type': 'date'}
#             ),
#             'gpa': forms.NumberInput(
#                 attrs={'step': '0.01', 'min': '0', 'max': '4.00'} # Kept validation attributes
#             ),
#         }
#
#
# class CertificationForm(forms.ModelForm):
#     """Form for certification entries."""
#
#     class Meta:
#         model = Certification
#         fields = [
#             'name', 'institute', 'completion_date',
#             'expiration_date', 'score', 'link', 'description'
#         ]
#          # Removed 'class' attributes from widgets, kept functional attrs
#         widgets = {
#             'name': forms.TextInput(),
#             'institute': forms.TextInput(),
#             'completion_date': forms.DateInput(
#                 attrs={'type': 'date'}
#             ),
#             'expiration_date': forms.DateInput(
#                 attrs={'type': 'date'}
#             ),
#             'score': forms.TextInput(),
#             'link': forms.URLInput(),
#             'description': forms.Textarea(
#                 attrs={'rows': 3}
#             ),
#         }
#
#
# class ProjectForm(forms.ModelForm):
#     """Form for project entries."""
#     # REMEMBER: Add 'is_current = forms.BooleanField(...)' here if needed
#
#     class Meta:
#         model = Project
#         # Add 'is_current' to fields if you add the field to the model
#         fields = [
#             'project_name', 'summary', 'start_date',
#             'completion_date', 'project_link', 'github_link'
#         ]
#          # Removed 'class' attributes from widgets, kept functional attrs
#         widgets = {
#             'project_name': forms.TextInput(),
#             'summary': forms.Textarea(
#                 attrs={'rows': 3}
#             ),
#             'start_date': forms.DateInput(
#                 attrs={'type': 'date'}
#             ),
#             'completion_date': forms.DateInput(
#                 attrs={'type': 'date'}
#             ),
#             'project_link': forms.URLInput(),
#             'github_link': forms.URLInput(),
#             # Add widget for 'is_current' if you add the field
#             # 'is_current': forms.CheckboxInput(attrs={'onchange': 'toggleCompletionDate(this)'}),
#         }
#
#
# class ProjectBulletPointForm(forms.ModelForm):
#     """Form for project bullet points."""
#     # Note: This form/formset might not be used based on previous analysis
#
#     class Meta:
#         model = ProjectBulletPoint
#         fields = ['description']
#         # Removed 'class' attributes from widgets
#         widgets = {
#             'description': forms.Textarea(
#                 attrs={'rows': 2}
#             ),
#         }
#
#
# class LanguageForm(forms.ModelForm):
#     """Form for language entries."""
#
#     class Meta:
#         model = Language
#         fields = ['language_name', 'proficiency']
#         # Removed 'class' attributes from widgets
#         widgets = {
#             'language_name': forms.TextInput(),
#             'proficiency': forms.Select(),
#         }
#
# # Note: This view function should ideally be in a views.py file
# def load_more_skills(request):
#     offset = int(request.GET.get('offset', 0))
#     limit = 20  # Number of skills to load each time
#     skills = Skill.objects.filter(user=request.user)[offset:offset+limit]
#     return render(request, 'resumes/partials/form_rows/skill_form_row.html', {'skills': skills})
#
#
# class CustomDataForm(forms.ModelForm):
#     """Form for custom sections like achievements, awards, etc."""
#
#     class Meta:
#         model = CustomData
#         fields = [
#             'name', 'completion_date', 'bullet_points',
#             'description', 'link', 'institution_name'
#         ]
#          # Removed 'class' attributes from widgets, kept functional attrs
#         widgets = {
#             'name': forms.TextInput(),
#             'completion_date': forms.DateInput(
#                 attrs={'type': 'date'}
#             ),
#             'bullet_points': forms.Textarea(
#                 attrs={
#                     'rows': 5,
#                     'placeholder': 'Add bullet points, one per line'
#                 }
#             ),
#             'description': forms.Textarea(
#                 attrs={'rows': 3}
#             ),
#             'link': forms.URLInput(),
#             'institution_name': forms.TextInput(),
#         }
#
#
# # Create formsets for related models
# # NOTE: Review if these specific formset definitions are actually used
# # in your views, especially the inlineformsets for bullet points,
# # and the modelformsets vs formset_factory usage in the wizard view.
#
# ExperienceBulletPointFormSet = inlineformset_factory(
#     Experience,
#     ExperienceBulletPoint,
#     form=ExperienceBulletPointForm,
#     extra=3,
#     can_delete=True
# )
#
# ProjectBulletPointFormSet = inlineformset_factory(
#     Project,
#     ProjectBulletPoint,
#     form=ProjectBulletPointForm,
#     extra=3,
#     can_delete=True
# )
#
# SkillFormSet = modelformset_factory(
#     Skill,
#     form=SkillForm,
#     extra=5,
#     can_delete=True
# )
#
# EducationFormSet = modelformset_factory(
#     Education,
#     form=EducationForm,
#     extra=1,
#     can_delete=True
# )
#
# CertificationFormSet = modelformset_factory(
#     Certification,
#     form=CertificationForm,
#     extra=1,
#     can_delete=True
# )
#
# LanguageFormSet = modelformset_factory(
#     Language,
#     form=LanguageForm,
#     extra=1,
#     can_delete=True
# )
#
#
# # # resumes/forms.py
# #
# # from django import forms
# # from django.forms import inlineformset_factory, modelformset_factory
# # from django.shortcuts import render
# #
# # from ..models import (
# #     Resume, Skill, Experience, ExperienceBulletPoint,
# #     Education, Certification, Project, ProjectBulletPoint,
# #     Language, CustomData
# # )
# #
# # from django import forms
# # from django.core.validators import FileExtensionValidator
# # from django.conf import settings
# #
# #
# #
# #
# #
# # class ResumeBasicInfoForm(forms.ModelForm):
# #     """Form for the basic personal information of the resume."""
# #
# #     class Meta:
# #         model = Resume
# #         fields = [
# #             'first_name', 'mid_name', 'last_name', 'email',
# #             'phone', 'address', 'linkedin', 'github', 'portfolio'
# #         ]
# #         widgets = {
# #             'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'mid_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
# #             'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'address': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
# #             'linkedin': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
# #             'github': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
# #             'portfolio': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
# #         }
# #
# #
# # class ResumeSummaryForm(forms.ModelForm):
# #     """Form for the professional summary of the resume."""
# #
# #     class Meta:
# #         model = Resume
# #         fields = ['summary']
# #         widgets = {
# #             'summary': forms.Textarea(
# #                 attrs={
# #                     'class': 'textarea textarea-bordered w-full',
# #                     'rows': 5,
# #                     'placeholder': 'Write a professional summary of your skills and experience (100 characters minimum)'
# #                 }
# #             ),
# #         }
# #
# #
# # class SkillForm(forms.ModelForm):
# #     """Form for individual skill entries."""
# #
# #     class Meta:
# #         model = Skill
# #         fields = ['skill_name', 'skill_type', 'proficiency_level']
# #         widgets = {
# #             'skill_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'skill_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
# #             'proficiency_level': forms.NumberInput(
# #                 attrs={
# #                     'class': 'range',
# #                     'min': '0',
# #                     'max': '100',
# #                     'step': '10',
# #                     'oninput': 'this.nextElementSibling.value = this.value'
# #                 }
# #             ),
# #         }
# #
# #
# # class ExperienceForm(forms.ModelForm):
# #     """Form for work experience entries."""
# #
# #     class Meta:
# #         model = Experience
# #         fields = [
# #             'job_title', 'employer', 'location',
# #             'start_date', 'end_date', 'is_current'
# #         ]
# #         widgets = {
# #             'job_title': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'employer': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'location': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'start_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'end_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'is_current': forms.CheckboxInput(
# #                 attrs={'class': 'checkbox', 'onchange': 'toggleEndDate(this)'}
# #             ),
# #         }
# #
# #
# # class ExperienceBulletPointForm(forms.ModelForm):
# #     """Form for experience bullet points."""
# #
# #     class Meta:
# #         model = ExperienceBulletPoint
# #         fields = ['description']
# #         widgets = {
# #             'description': forms.Textarea(
# #                 attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}
# #             ),
# #         }
# #
# #
# # class EducationForm(forms.ModelForm):
# #     """Form for education entries."""
# #
# #     class Meta:
# #         model = Education
# #         fields = [
# #             'school_name', 'location', 'degree',
# #             'degree_type', 'field_of_study',
# #             'graduation_date', 'gpa'
# #         ]
# #         widgets = {
# #             'school_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'location': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'degree': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'degree_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
# #             'field_of_study': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'graduation_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'gpa': forms.NumberInput(
# #                 attrs={'class': 'input input-bordered w-full', 'step': '0.01', 'min': '0', 'max': '4.00'}
# #             ),
# #         }
# #
# #
# # class CertificationForm(forms.ModelForm):
# #     """Form for certification entries."""
# #
# #     class Meta:
# #         model = Certification
# #         fields = [
# #             'name', 'institute', 'completion_date',
# #             'expiration_date', 'score', 'link', 'description'
# #         ]
# #         widgets = {
# #             'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'institute': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'completion_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'expiration_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'score': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'link': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
# #             'description': forms.Textarea(
# #                 attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}
# #             ),
# #         }
# #
# #
# # class ProjectForm(forms.ModelForm):
# #     """Form for project entries."""
# #
# #     class Meta:
# #         model = Project
# #         fields = [
# #             'project_name', 'summary', 'start_date',
# #             'completion_date', 'project_link', 'github_link'
# #         ]
# #         widgets = {
# #             'project_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'summary': forms.Textarea(
# #                 attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}
# #             ),
# #             'start_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'completion_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'project_link': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
# #             'github_link': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
# #         }
# #
# #
# # class ProjectBulletPointForm(forms.ModelForm):
# #     """Form for project bullet points."""
# #
# #     class Meta:
# #         model = ProjectBulletPoint
# #         fields = ['description']
# #         widgets = {
# #             'description': forms.Textarea(
# #                 attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}
# #             ),
# #         }
# #
# #
# # class LanguageForm(forms.ModelForm):
# #     """Form for language entries."""
# #
# #     class Meta:
# #         model = Language
# #         fields = ['language_name', 'proficiency']
# #         widgets = {
# #             'language_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'proficiency': forms.Select(attrs={'class': 'select select-bordered w-full'}),
# #         }
# #
# # def load_more_skills(request):
# #     offset = int(request.GET.get('offset', 0))
# #     limit = 20  # Number of skills to load each time
# #     skills = Skill.objects.filter(user=request.user)[offset:offset+limit]
# #     return render(request, 'resumes/theme_partials/skill_form_row.html', {'skills': skills})
# #
# #
# # class CustomDataForm(forms.ModelForm):
# #     """Form for custom sections like achievements, awards, etc."""
# #
# #     class Meta:
# #         model = CustomData
# #         fields = [
# #             'name', 'completion_date', 'bullet_points',
# #             'description', 'link', 'institution_name'
# #         ]
# #         widgets = {
# #             'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #             'completion_date': forms.DateInput(
# #                 attrs={'class': 'input input-bordered w-full', 'type': 'date'}
# #             ),
# #             'bullet_points': forms.Textarea(
# #                 attrs={
# #                     'class': 'textarea textarea-bordered w-full',
# #                     'rows': 5,
# #                     'placeholder': 'Add bullet points, one per line'
# #                 }
# #             ),
# #             'description': forms.Textarea(
# #                 attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}
# #             ),
# #             'link': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
# #             'institution_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
# #         }
# #
# #
# # # Create formsets for related models
# # ExperienceBulletPointFormSet = inlineformset_factory(
# #     Experience,
# #     ExperienceBulletPoint,
# #     form=ExperienceBulletPointForm,
# #     extra=3,
# #     can_delete=True
# # )
# #
# # ProjectBulletPointFormSet = inlineformset_factory(
# #     Project,
# #     ProjectBulletPoint,
# #     form=ProjectBulletPointForm,
# #     extra=3,
# #     can_delete=True
# # )
# #
# # SkillFormSet = modelformset_factory(
# #     Skill,
# #     form=SkillForm,
# #     extra=5,
# #     can_delete=True
# # )
# #
# # EducationFormSet = modelformset_factory(
# #     Education,
# #     form=EducationForm,
# #     extra=1,
# #     can_delete=True
# # )
# #
# # CertificationFormSet = modelformset_factory(
# #     Certification,
# #     form=CertificationForm,
# #     extra=1,
# #     can_delete=True
# # )
# #
# # LanguageFormSet = modelformset_factory(
# #     Language,
# #     form=LanguageForm,
# #     extra=1,
# #     can_delete=True
# # )