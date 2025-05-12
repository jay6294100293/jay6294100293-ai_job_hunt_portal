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