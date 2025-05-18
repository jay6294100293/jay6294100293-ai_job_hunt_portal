# job_portal/views/finalize_resume_view.py (Formerly generate_resume_view.py)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.db import transaction
from django.utils import timezone  # If you add a 'published_at' field
import logging

from job_portal.models import Resume

logger = logging.getLogger(__name__)


@login_required
def finalize_resume_view(request, resume_id):
    """
    Finalizes a draft resume, changing its status from 'draft' to 'active'.
    Assumes all data has been incrementally saved to the database via editing views.
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if resume.status != 'draft':
        messages.info(request, f"Resume '{resume.title}' is already {resume.get_status_display()}.")
        return redirect('job_portal:view_resume', resume_id=resume.id)  # Ensure 'view_resume' URL exists

    if request.method == 'POST':  # Confirmation step
        try:
            with transaction.atomic():
                resume.status = 'active'  # Set to your "finalized" status
                resume.updated_at = timezone.now()  # Ensure updated_at is current
                # Optionally: resume.published_at = timezone.now()
                resume.save()
            messages.success(request, f"Resume '{resume.title}' has been finalized and is now active!")
            return redirect('job_portal:view_resume', resume_id=resume.id)
        except Exception as e:
            logger.error(f"Error finalizing resume {resume_id} for user {request.user.username}: {e}", exc_info=True)
            messages.error(request, f"An unexpected error occurred while finalizing the resume: {str(e)}")
            # Redirect back to view the resume (still in draft) or dashboard
            return redirect('job_portal:view_resume', resume_id=resume.id)

    # For GET request, display a confirmation page.
    # Ensure 'resumes/confirm_finalize_resume.html' template exists.
    return render(request, 'resumes/confirm_finalize_resume.html', {'resume': resume})

# # resumes/views.py
#
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.shortcuts import redirect
#
# from job_portal.models import (
#     Resume, Skill, Experience, ExperienceBulletPoint,
#     Education, Certification, Project, ProjectBulletPoint,
#     Language, CustomData
# )
#
#
# @login_required
# def generate_resume(request):
#     """Generate the final resume based on all the collected data."""
#     # Get resume data from session
#     form_data = request.session.get('resume_form_data', {})
#     template_id = request.session.get('resume_template_id')
#
#     if not form_data or not template_id:
#         messages.error(request, "Missing resume data. Please start over.")
#         return redirect('job_portal:template_selection')
#
#     try:
#         with transaction.atomic():
#             # Create the Resume object
#             personal_info = form_data.get('personal_info', {})
#
#             # Fix for the summary field - handle both string and dict cases
#             summary = form_data.get('summary', '')
#
#             # Check if summary is a string or dict and handle accordingly
#             if isinstance(summary, dict):
#                 summary_text = summary.get('summary', '')
#             else:
#                 summary_text = summary  # Use the summary string directly
#
#             resume = Resume(
#                 first_name=personal_info.get('first_name', ''),
#                 mid_name=personal_info.get('mid_name', ''),
#                 last_name=personal_info.get('last_name', ''),
#                 email=personal_info.get('email', ''),
#                 phone=personal_info.get('phone', ''),
#                 address=personal_info.get('address', ''),
#                 linkedin=personal_info.get('linkedin', ''),
#                 github=personal_info.get('github', ''),
#                 portfolio=personal_info.get('portfolio', ''),
#                 summary=summary_text,  # Use the correctly extracted summary
#                 user=request.user,
#                 status='generated'
#             )
#             resume.save()
#
#             # Process skills
#             for skill_data in form_data.get('skills', []):
#                 Skill.objects.create(
#                     resume=resume,
#                     skill_name=skill_data.get('skill_name', ''),
#                     skill_type=skill_data.get('skill_type', 'technical'),
#                     proficiency_level=skill_data.get('proficiency_level', 0)
#                 )
#
#             # Process experiences
#             for exp_data in form_data.get('experiences', []):
#                 experience = Experience.objects.create(
#                     resume=resume,
#                     job_title=exp_data.get('job_title', ''),
#                     employer=exp_data.get('employer', ''),
#                     location=exp_data.get('location', ''),
#                     start_date=exp_data.get('start_date') or None,
#                     end_date=exp_data.get('end_date') or None,
#                     is_current=exp_data.get('is_current', False)
#                 )
#
#                 # Add bullet points
#                 for bullet_data in exp_data.get('bullet_points', []):
#                     bullet_text = bullet_data
#                     # Handle both string and dict formats for bullet points
#                     if isinstance(bullet_data, dict):
#                         bullet_text = bullet_data.get('description', '')
#
#                     if bullet_text:
#                         ExperienceBulletPoint.objects.create(
#                             experience=experience,
#                             description=bullet_text
#                         )
#
#             # Process education
#             for edu_data in form_data.get('educations', []):
#                 Education.objects.create(
#                     resume=resume,
#                     school_name=edu_data.get('school_name', ''),
#                     location=edu_data.get('location', ''),
#                     degree=edu_data.get('degree', ''),
#                     degree_type=edu_data.get('degree_type', 'bachelor'),
#                     field_of_study=edu_data.get('field_of_study', ''),
#                     graduation_date=edu_data.get('graduation_date') or None,
#                     gpa=edu_data.get('gpa') or None
#                 )
#
#             # Process projects
#             for proj_data in form_data.get('projects', []):
#                 project = Project.objects.create(
#                     resume=resume,
#                     project_name=proj_data.get('project_name', ''),
#                     summary=proj_data.get('summary', ''),
#                     start_date=proj_data.get('start_date') or None,
#                     completion_date=proj_data.get('completion_date') or None,
#                     project_link=proj_data.get('project_link', ''),
#                     github_link=proj_data.get('github_link', '')
#                 )
#
#                 # Add bullet points
#                 for bullet_text in proj_data.get('bullet_points', []):
#                     if bullet_text:
#                         ProjectBulletPoint.objects.create(
#                             project=project,
#                             description=bullet_text
#                         )
#
#             # Process certifications
#             for cert_data in form_data.get('certifications', []):
#                 Certification.objects.create(
#                     resume=resume,
#                     name=cert_data.get('name', ''),
#                     institute=cert_data.get('institute', ''),
#                     completion_date=cert_data.get('completion_date') or None,
#                     expiration_date=cert_data.get('expiration_date') or None,
#                     score=cert_data.get('score', ''),
#                     link=cert_data.get('link', ''),
#                     description=cert_data.get('description', '')
#                 )
#
#             # Process languages
#             for lang_data in form_data.get('languages', []):
#                 Language.objects.create(
#                     resume=resume,
#                     language_name=lang_data.get('language_name', ''),
#                     proficiency=lang_data.get('proficiency', 'basic')
#                 )
#
#             # Process custom sections
#             for custom_data in form_data.get('custom_sections', []):
#                 if custom_data.get('name'):
#                     CustomData.objects.create(
#                         resume=resume,
#                         name=custom_data.get('name', ''),
#                         completion_date=custom_data.get('completion_date') or None,
#                         bullet_points=custom_data.get('bullet_points', ''),
#                         description=custom_data.get('description', ''),
#                         link=custom_data.get('link', ''),
#                         institution_name=custom_data.get('institution_name', '')
#                     )
#
#             # Clear session data
#             request.session['resume_form_data'] = {}
#             request.session['resume_template_id'] = None
#             request.session['resume_wizard_step'] = None
#
#             messages.success(request, "Resume successfully created!")
#
#             # Redirect to view the generated resume
#             return redirect('job_portal:view_resume', resume_id=resume.id)
#
#     except Exception as e:
#         messages.error(request, f"Error generating resume: {str(e)}")
#         return redirect('job_portal:template_selection')