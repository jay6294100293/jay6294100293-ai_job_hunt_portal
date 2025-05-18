# resumes/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from job_portal.models import (
    Resume
)


@login_required
def view_resume(request, resume_id):
    """View the generated resume."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_id = request.GET.get('template', 1)  # Default to template 1

    context = {
        'resume': resume,
        'template_id': template_id,
    }

    return render(request, f'resumes/templates/template{template_id}.html', context)