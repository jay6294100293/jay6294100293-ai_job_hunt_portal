# job_portal/views/download_resume_view.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from job_portal.models import Resume


@login_required
def download_resume(request, resume_id):
    """Download the resume as PDF."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # Check if the resume is published - only allow downloads of published resumes
    if resume.publication_status != Resume.PUBLISHED:
        messages.warning(request, "You can only download published resumes. Please finalize this resume first.")
        return HttpResponseRedirect(reverse('job_portal:view_resume', args=[resume_id]))

    # Check if there's an output file already generated
    if resume.output_file:
        # Use the existing file
        file_path = resume.output_file.path
        filename = resume.output_file.name.split('/')[-1]
    else:
        # No output file yet, so generate one
        template_id = resume.template_name if resume.template_name else request.GET.get('template', 1)

        # Here you would implement PDF generation logic using a library like WeasyPrint
        # For example code purposes, we'll just show a placeholder:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume.full_name}_Resume.pdf"'

        # PDF generation logic would go here
        # from weasyprint import HTML
        # html = render_to_string(f'resumes/templates/template{template_id}.html', {'resume': resume})
        # pdf = HTML(string=html).write_pdf()
        # response.write(pdf)

        messages.success(request, "Resume downloaded successfully!")
        return response

    # If we have a file path, serve the file
    with open(file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

    messages.success(request, "Resume downloaded successfully!")
    return response

# # resumes/views.py
#
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404


#
# from job_portal.models import (
#     Resume
# )
#
#
# @login_required
# def download_resume(request, resume_id):
#     """Download the resume as PDF."""
#     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
#     template_id = request.GET.get('template', 1)
#
#     # Here you would implement PDF generation logic
#     # For example, using a library like WeasyPrint
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{resume.full_name}_Resume.pdf"'
#
#     # PDF generation logic would go here
#     # This is a placeholder for where you'd add the PDF generation logic
#
#     messages.success(request, "Resume downloaded successfully!")
#     return response