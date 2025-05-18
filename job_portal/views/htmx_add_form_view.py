# job_portal/views/htmx_add_form_view.py

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Import the forms that will be dynamically added
from job_portal.forms.resume_creation_form import (
    SkillForm, ExperienceForm, EducationForm, ProjectForm,
    CertificationForm, LanguageForm, CustomDataForm,
    ExperienceBulletPointForm, ProjectBulletPointForm
)


@login_required
@require_http_methods(["GET"])
def htmx_add_form_row(request):
    """
    HTMX handler for adding a new, empty form row dynamically for various resume sections.
    It renders a partial template, passing an unbound form instance with a '__prefix__'
    to be compatible with Django formset management.
    """
    form_type = request.GET.get('form_type')
    # '__prefix__' is the standard placeholder Django formsets use for new forms.
    # Client-side JavaScript will replace this with the correct numeric index.
    form_index_placeholder = request.GET.get('index', '__prefix__')

    # parent_index is relevant for nested formsets (e.g., bullet points within an experience)
    # It would typically be the numeric index of the parent form in its formset.
    parent_index = request.GET.get('parent_index')

    if not form_type:
        return HttpResponseBadRequest("Form type parameter ('form_type') not specified.")

    context = {'index': form_index_placeholder, 'parent_index': parent_index}
    template_name = None
    form_instance = None  # This will be an unbound form

    # Determine the formset prefix based on how forms are defined
    # Example: ExperienceInlineFormSet(..., prefix='exp') means new experience forms are exp-__prefix__-job_title
    if form_type == 'skill':
        form_instance = SkillForm(prefix=f'skill-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/skill_form_row.html'
    elif form_type == 'experience':
        form_instance = ExperienceForm(prefix=f'exp-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/experience_form_row.html'
    elif form_type == 'education':
        form_instance = EducationForm(prefix=f'edu-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/education_form_row.html'
    elif form_type == 'project':
        form_instance = ProjectForm(prefix=f'proj-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/project_form_row.html'
    elif form_type == 'certification':
        form_instance = CertificationForm(prefix=f'cert-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/certification_form_row.html'
    elif form_type == 'language':
        form_instance = LanguageForm(prefix=f'lang-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/language_form_row.html'
    elif form_type == 'custom_data':
        form_instance = CustomDataForm(prefix=f'custom-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/custom_section_form_row.html'  # Ensure template exists
    elif form_type == 'experience_bullet_point':
        if parent_index is None:  # parent_index (e.g., 'exp-0') must be provided
            return HttpResponseBadRequest("Parent index ('parent_index') required for experience bullet point.")
        # The prefix for nested formsets is more complex: parent_formset_prefix-parent_index-nested_formset_field_name-__prefix__
        # Example: exp-0-bullet_points-__prefix__-bullet_point
        # For simplicity, the template for experience_form_row.html might handle the bullet point sub-formset directly.
        # Or, this specific HTMX call is for adding one bullet to an *existing* experience.
        form_instance = ExperienceBulletPointForm(prefix=f'exp_bullet-{parent_index}-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/bullet_point_form_row.html'  # Or specific
    elif form_type == 'project_bullet_point':
        if parent_index is None:
            return HttpResponseBadRequest("Parent index ('parent_index') required for project bullet point.")
        form_instance = ProjectBulletPointForm(prefix=f'proj_bullet-{parent_index}-{form_index_placeholder}')
        template_name = 'resumes/partials/form_rows/bullet_point_form_row.html'  # Or specific

    if template_name and form_instance:
        context['form'] = form_instance  # Pass the unbound form to the template
        return render(request, template_name, context)
    else:
        return HttpResponseBadRequest(f"Unsupported form type ('{form_type}') or missing required parameters.")

# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import render
# from django.views.decorators.http import require_http_methods
#
# from job_portal.models import (
#     Skill, Education, Language
# )
#
#
# @login_required
# @require_http_methods(["GET"])
# def htmx_add_form_row(request):
#     """HTMX handler for adding a new form row dynamically."""
#     form_type = request.GET.get('form_type')
#     index = int(request.GET.get('index', 0))
#
#     context = {'index': index}
#
#     if form_type == 'skill':
#         # Handle skill addition specifically
#         skill_name = request.GET.get('skill_name', '')
#         skill_type = request.GET.get('skill_type', '')
#         proficiency = request.GET.get('proficiency', '50')
#         years = request.GET.get('years', '')
#
#         context.update({
#             'skill_types': dict(Skill.SKILL_TYPES),
#             'skill_name': skill_name,
#             'skill_type': skill_type,
#             'proficiency': proficiency,
#             'years': years
#         })
#
#         # Return the skill card instead of a form row
#         return render(request, 'resumes/partials/skill_form_row.html', context)
#     elif form_type == 'experience':
#         return render(request, 'resumes/partials/experience_form_row.html', context)
#     elif form_type == 'education':
#         context['degree_types'] = dict(Education.DEGREE_TYPES)
#         return render(request, 'resumes/partials/education_form_row.html', context)
#     elif form_type == 'project':
#         return render(request, 'resumes/partials/project_form_row.html', context)
#     elif form_type == 'certification':
#         return render(request, 'resumes/partials/certification_form_row.html', context)
#     elif form_type == 'language':
#         context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
#         return render(request, 'resumes/partials/language_form_row.html', context)
#     elif form_type == 'custom_section':
#         return render(request, 'resumes/partials/custom_section_form_row.html', context)
#     elif form_type == 'bullet_point':
#         parent_index = request.GET.get('parent_index', 0)
#         ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Add AI engine parameter
#         context.update({
#             'parent_index': parent_index,
#             'ai_engine': ai_engine  # Pass the AI engine to the template
#         })
#         return render(request, 'resumes/partials/bullet_point_form_row.html', context)
#
#     return HttpResponse("Form type not recognized")
