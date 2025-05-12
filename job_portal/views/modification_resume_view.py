# resumes/views.py
import json
import os
import tempfile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods

from job_portal.models import (
    Resume, Skill, Experience, ExperienceBulletPoint,
    Education, Certification, Project, ProjectBulletPoint,
    Language, CustomData, APIUsage
)
from services.bullets_ai_services import generate_bullets_chatgpt, get_template_bullets, generate_bullets_gemini, \
    enhance_bullet_chatgpt, enhance_bullet_gemini, enhance_bullet_basic, ats_optimize_chatgpt, ats_optimize_gemini
# from ..forms.resume_creation_form import ResumeBasicInfoForm, ResumeSummaryForm
from ..forms.resume_upload_form import ResumeUploadForm
from ..models import (
    JobInput
)
from django.contrib.auth.decorators import login_required









@login_required
def resume_list(request):
    """List all resumes created by the user."""
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})


@login_required
def edit_resume(request, resume_id):
    """Edit an existing resume."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # Load resume data into session for the wizard
    form_data = {}

    # Personal Info
    form_data['personal_info'] = {
        'first_name': resume.first_name,
        'mid_name': resume.mid_name,
        'last_name': resume.last_name,
        'email': resume.email,
        'phone': resume.phone,
        'address': resume.address,
        'linkedin': resume.linkedin,
        'github': resume.github,
        'portfolio': resume.portfolio,
    }

    # Summary
    form_data['summary'] = {
        'summary': resume.summary,
    }

    # Skills
    skills_data = []
    for skill in resume.skills.all():
        skills_data.append({
            'skill_name': skill.skill_name,
            'skill_type': skill.skill_type,
            'proficiency_level': skill.proficiency_level,
        })
    form_data['skills'] = skills_data

    experiences_data = []
    for exp in resume.experiences.all():
        bullet_points = [{'description': bp.description} for bp in exp.bullet_points.all()]
        experiences_data.append({
            'job_title': exp.job_title,
            'employer': exp.employer,
            'location': exp.location,
            'start_date': exp.start_date,
            'end_date': exp.end_date,
            'is_current': exp.is_current,
            'bullet_points': bullet_points,  # Now a list of dicts with description
        })
    form_data['experiences'] = experiences_data

    # Education
    educations_data = []
    for edu in resume.educations.all():
        educations_data.append({
            'school_name': edu.school_name,
            'location': edu.location,
            'degree': edu.degree,
            'degree_type': edu.degree_type,
            'field_of_study': edu.field_of_study,
            'graduation_date': edu.graduation_date,
            'gpa': edu.gpa,
        })
    form_data['educations'] = educations_data

    # Projects
    projects_data = []
    for proj in resume.projects.all():
        bullet_points = [bp.description for bp in proj.bullet_points.all()]
        projects_data.append({
            'project_name': proj.project_name,
            'summary': proj.summary,
            'start_date': proj.start_date,
            'completion_date': proj.completion_date,
            'project_link': proj.project_link,
            'github_link': proj.github_link,
            'bullet_points': bullet_points,
        })
    form_data['projects'] = projects_data

    # Certifications
    certifications_data = []
    for cert in resume.certifications.all():
        certifications_data.append({
            'name': cert.name,
            'institute': cert.institute,
            'completion_date': cert.completion_date,
            'expiration_date': cert.expiration_date,
            'score': cert.score,
            'link': cert.link,
            'description': cert.description,
        })
    form_data['certifications'] = certifications_data

    # Languages
    languages_data = []
    for lang in resume.languages.all():
        languages_data.append({
            'language_name': lang.language_name,
            'proficiency': lang.proficiency,
        })
    form_data['languages'] = languages_data

    # Custom Sections
    custom_sections_data = []
    for section in resume.custom_data.all():
        custom_sections_data.append({
            'name': section.name,
            'completion_date': section.completion_date,
            'bullet_points': section.bullet_points,
            'description': section.description,
            'link': section.link,
            'institution_name': section.institution_name,
        })
    form_data['custom_sections'] = custom_sections_data

    # Store data in session
    request.session['resume_form_data'] = form_data
    request.session['resume_template_id'] = request.GET.get('template', '1')
    request.session['edit_resume_id'] = resume_id

    # Redirect to first step of wizard
    return redirect('job_portal:resume_wizard', step=1)


@login_required
def delete_resume(request, resume_id):
    """Delete a resume."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if request.method == 'POST':
        resume.delete()
        messages.success(request, "Resume deleted successfully")
        return redirect('job_portal:resume_list')

    return render(request, 'resumes/confirm_delete.html', {'resume': resume})

@login_required
@require_http_methods(["POST"])
def update_resume_ajax(request, resume_id):
    """AJAX handler for updating resume section."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    section = request.POST.get('section')
    data = json.loads(request.POST.get('data', '{}'))

    try:
        if section == 'personal_info':
            for field, value in data.items():
                if hasattr(resume, field):
                    setattr(resume, field, value)
            resume.save()
        elif section == 'skills':
            # Clear existing skills and add new ones
            resume.skills.all().delete()
            for skill_data in data:
                Skill.objects.create(
                    resume=resume,
                    skill_name=skill_data.get('skill_name', ''),
                    skill_type=skill_data.get('skill_type', 'technical'),
                    proficiency_level=skill_data.get('proficiency_level', 0)
                )
        elif section == 'work_experience':
            # Clear existing work experiences and add new ones
            resume.experiences.all().delete()
            for exp_data in data:
                # Create the main experience entry
                experience = Experience.objects.create(
                    resume=resume,
                    company=exp_data.get('company', ''),
                    position=exp_data.get('position', ''),
                    location=exp_data.get('location', ''),
                    start_date=exp_data.get('start_date', None),
                    end_date=exp_data.get('end_date', None),
                    is_current=exp_data.get('is_current', False)
                )

                # Add bullet points/responsibilities
                for bullet in exp_data.get('responsibilities', []):
                    ExperienceBulletPoint.objects.create(
                        experience=experience,
                        description=bullet
                    )
        elif section == 'education':
            # Clear existing education entries and add new ones
            resume.educations.all().delete()
            for edu_data in data:
                Education.objects.create(
                    resume=resume,
                    institution=edu_data.get('institution', ''),
                    degree=edu_data.get('degree', ''),
                    field_of_study=edu_data.get('field_of_study', ''),
                    location=edu_data.get('location', ''),
                    start_date=edu_data.get('start_date', None),
                    end_date=edu_data.get('end_date', None),
                    is_current=edu_data.get('is_current', False),
                    gpa=edu_data.get('gpa', None),
                    highlights=edu_data.get('highlights', '')
                )
        elif section == 'projects':
            # Clear existing projects and add new ones
            resume.projects.all().delete()
            for proj_data in data:
                # Create the main project entry
                project = Project.objects.create(
                    resume=resume,
                    title=proj_data.get('title', ''),
                    description=proj_data.get('description', ''),
                    url=proj_data.get('url', ''),
                    start_date=proj_data.get('start_date', None),
                    end_date=proj_data.get('end_date', None),
                    is_current=proj_data.get('is_current', False)
                )

                # Add bullet points/highlights
                for bullet in proj_data.get('highlights', []):
                    ProjectBulletPoint.objects.create(
                        project=project,
                        description=bullet
                    )
        elif section == 'certifications':
            # Clear existing certifications and add new ones
            resume.certifications.all().delete()
            for cert_data in data:
                Certification.objects.create(
                    resume=resume,
                    name=cert_data.get('name', ''),
                    issuing_organization=cert_data.get('issuing_organization', ''),
                    issue_date=cert_data.get('issue_date', None),
                    expiration_date=cert_data.get('expiration_date', None),
                    credential_id=cert_data.get('credential_id', ''),
                    credential_url=cert_data.get('credential_url', '')
                )
        elif section == 'languages':
            # Clear existing languages and add new ones
            resume.languages.all().delete()
            for lang_data in data:
                Language.objects.create(
                    resume=resume,
                    language=lang_data.get('language', ''),
                    proficiency=lang_data.get('proficiency', 'basic')
                )
        elif section == 'summary':
            # Update the professional summary
            resume.summary = data.get('summary', '')
            resume.save()
        elif section == 'contact_info':
            # Update contact information
            resume.email = data.get('email', resume.email)
            resume.phone = data.get('phone', resume.phone)
            resume.website = data.get('website', resume.website)
            resume.linkedin = data.get('linkedin', resume.linkedin)
            resume.github = data.get('github', resume.github)
            resume.address = data.get('address', resume.address)
            resume.city = data.get('city', resume.city)
            resume.state = data.get('state', resume.state)
            resume.zip_code = data.get('zip_code', resume.zip_code)
            resume.country = data.get('country', resume.country)
            resume.save()
        elif section == 'additional_sections':
            # Handle custom sections
            resume.additional_sections.all().delete()
            for section_data in data:
                custom_section = CustomData.objects.create(
                    resume=resume,
                    title=section_data.get('title', ''),
                    order=section_data.get('order', 0)
                )

                # Add items to the custom section
                for item in section_data.get('items', []):
                    CustomData.objects.create(
                        section=custom_section,
                        content=item
                    )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})