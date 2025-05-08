from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from job_portal.models import (
    Skill, Education, Language
)


@login_required
@require_http_methods(["GET"])
def htmx_add_form_row(request):
    """HTMX handler for adding a new form row dynamically."""
    form_type = request.GET.get('form_type')
    index = int(request.GET.get('index', 0))

    context = {'index': index}

    if form_type == 'skill':
        # Handle skill addition specifically
        skill_name = request.GET.get('skill_name', '')
        skill_type = request.GET.get('skill_type', '')
        proficiency = request.GET.get('proficiency', '50')
        years = request.GET.get('years', '')

        context.update({
            'skill_types': dict(Skill.SKILL_TYPES),
            'skill_name': skill_name,
            'skill_type': skill_type,
            'proficiency': proficiency,
            'years': years
        })

        # Return the skill card instead of a form row
        return render(request, 'resumes/partials/skill_form_row.html', context)
    elif form_type == 'experience':
        return render(request, 'resumes/partials/experience_form_row.html', context)
    elif form_type == 'education':
        context['degree_types'] = dict(Education.DEGREE_TYPES)
        return render(request, 'resumes/partials/education_form_row.html', context)
    elif form_type == 'project':
        return render(request, 'resumes/partials/project_form_row.html', context)
    elif form_type == 'certification':
        return render(request, 'resumes/partials/certification_form_row.html', context)
    elif form_type == 'language':
        context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
        return render(request, 'resumes/partials/language_form_row.html', context)
    elif form_type == 'custom_section':
        return render(request, 'resumes/partials/custom_section_form_row.html', context)
    elif form_type == 'bullet_point':
        parent_index = request.GET.get('parent_index', 0)
        ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Add AI engine parameter
        context.update({
            'parent_index': parent_index,
            'ai_engine': ai_engine  # Pass the AI engine to the template
        })
        return render(request, 'resumes/partials/bullet_point_form_row.html', context)

    return HttpResponse("Form type not recognized")
