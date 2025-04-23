# resumes/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from job_portal.models import (
    Resume
)


@login_required
def download_resume(request, resume_id):
    """Download the resume as PDF."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_id = request.GET.get('template', 1)

    # Here you would implement PDF generation logic
    # For example, using a library like WeasyPrint

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.full_name}_Resume.pdf"'

    # PDF generation logic would go here
    # This is a placeholder for where you'd add the PDF generation logic

    messages.success(request, "Resume downloaded successfully!")
    return response