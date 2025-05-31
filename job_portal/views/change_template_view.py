from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from job_portal.models import Resume


@login_required
def change_template_view(request, resume_id):
    """View to change the template of an existing resume."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if request.method == 'POST':
        template_id = request.POST.get('template_id')

        if not template_id:
            messages.error(request, 'Please select a template.')
            return redirect('job_portal:change_template', resume_id=resume_id)

        try:
            # Update the resume template (adjust field names based on your model)
            resume.template_name = template_id  # or however you store template info
            resume.save()

            messages.success(request, 'Resume template updated successfully!')

            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Template updated successfully!'
                })

            return redirect('job_portal:view_resume', resume_id=resume.id)

        except Exception as e:
            messages.error(request, 'Failed to update template. Please try again.')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to update template. Please try again.'
                })

    # GET request - show template selection page
    templates = [
        {'id': 'modern', 'name': 'Modern Professional'},
        {'id': 'classic', 'name': 'Classic Traditional'},
        {'id': 'creative', 'name': 'Creative Designer'},
        {'id': 'minimal', 'name': 'Minimal Clean'},
    ]

    context = {
        'resume': resume,
        'templates': templates,
    }

    return render(request, 'job_portal/change_template.html', context)