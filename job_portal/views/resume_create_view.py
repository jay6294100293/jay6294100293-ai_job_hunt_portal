# resumes/views.py

import json
import os
import tempfile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from services.bullets_ai_services import generate_bullets_chatgpt, get_template_bullets, generate_bullets_gemini, \
    enhance_bullet_chatgpt, enhance_bullet_gemini, enhance_bullet_basic, ats_optimize_chatgpt, ats_optimize_gemini
from ..forms.resume_creation_form import ResumeBasicInfoForm, ResumeSummaryForm
from ..models import (
    Resume, Skill, Experience, ExperienceBulletPoint,
    Education, Certification, Project, ProjectBulletPoint,
    Language, CustomData, APIUsage, JobInput
)


# job_portal/views/resume_views.py


@login_required
@login_required
def template_selection(request):
    """Display template options for user to select."""
    templates = [
        {
            'id': 1,
            'name': 'Professional',
            'description': 'A clean and professional template suitable for corporate roles',
            'thumbnail': 'img/templates/1.jpg',
        },
        {
            'id': 2,
            'name': 'Creative',
            'description': 'A modern, creative template perfect for design roles',
            'thumbnail': 'img/templates/2.jpg',
        },
        {
            'id': 3,
            'name': 'Minimal',
            'description': 'A minimalist template focusing on content clarity',
            'thumbnail': 'img/templates/3.jpg',
        },
        {
            'id': 4,
            'name': 'Academic',
            'description': 'A comprehensive template for academic positions',
            'thumbnail': 'img/templates/4.jpg',
        },
        {
            'id': 5,
            'name': 'Technical',
            'description': 'A technical-focused template for IT professionals',
            'thumbnail': 'img/templates/5.jpg',
        },
        {
            'id': 6,
            'name': 'Fresh Graduate',
            'description': 'Perfect for recent graduates and entry-level professionals',
            'thumbnail': 'img/templates/6.jpg',
        },
    ]

    return render(request, 'resumes/template_select.html', {'templates': templates})


from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["POST"])
def select_template(request):
    """Save the selected template to session and redirect to form wizard."""
    template_id = request.POST.get('template_id')
    if not template_id:
        messages.error(request, "Please select a template")
        return redirect('job_portal:select_template')

    request.session['resume_template_id'] = template_id
    request.session['resume_wizard_step'] = 1

    # Initialize a new session for storing form data
    request.session['resume_form_data'] = {}

    # Redirect to the first step of the wizard
    return redirect('job_portal:resume_wizard', step=1)


@login_required
def resume_wizard(request, step):
    """Handle the multi-step form wizard for resume creation."""
    # Get the stored template_id
    template_id = request.session.get('resume_template_id')
    if not template_id:
        messages.error(request, "Please select a template first")
        return redirect('job_portal:template_selection')

    # Initialize or get the form data from session
    form_data = request.session.get('resume_form_data', {})

    # Define the steps and corresponding forms
    steps = {
        1: {
            'title': 'Personal Information',
            'form_class': ResumeBasicInfoForm,
            'template': 'resumes/wizard_steps/personal_info.html',
        },
        2: {
            'title': 'Professional Summary',
            'form_class': ResumeSummaryForm,
            'template': 'resumes/wizard_steps/summary.html',
        },
        3: {
            'title': 'Skills',
            'form_class': None,  # Using formset
            'template': 'resumes/wizard_steps/skills.html',
        },
        4: {
            'title': 'Work Experience',
            'form_class': None,  # Special handling for experience + bullet points
            'template': 'resumes/wizard_steps/experience.html',
        },
        5: {
            'title': 'Education',
            'form_class': None,  # Using formset
            'template': 'resumes/wizard_steps/education.html',
        },
        6: {
            'title': 'Projects',
            'form_class': None,  # Special handling for projects + bullet points
            'template': 'resumes/wizard_steps/projects.html',
        },
        7: {
            'title': 'Certifications',
            'form_class': None,  # Using formset
            'template': 'resumes/wizard_steps/certifications.html',
        },
        8: {
            'title': 'Languages',
            'form_class': None,  # Using formset
            'template': 'resumes/wizard_steps/languages.html',
        },
        9: {
            'title': 'Additional Sections',
            'form_class': None,  # Using formset for CustomData
            'template': 'resumes/wizard_steps/custom_sections.html',
        },
    }

    try:
        step = int(step)
        if step < 1 or step > len(steps):
            return redirect('job_portal:resume_wizard', step=1)
    except ValueError:
        return redirect('job_portal:resume_wizard', step=1)

    # Store current step in session
    request.session['resume_wizard_step'] = step

    # Handle specific step logic
    if step == 1:  # Personal Information
        return handle_personal_info_step(request, steps, step, form_data)
    elif step == 2:  # Professional Summary
        return handle_summary_step(request, steps, step, form_data)
    elif step == 3:  # Skills
        return handle_skills_step(request, steps, step, form_data)
    elif step == 4:  # Work Experience
        return handle_experience_step(request, steps, step, form_data)
    elif step == 5:  # Education
        return handle_education_step(request, steps, step, form_data)
    elif step == 6:  # Projects
        return handle_projects_step(request, steps, step, form_data)
    elif step == 7:  # Certifications
        return handle_certifications_step(request, steps, step, form_data)
    elif step == 8:  # Languages
        return handle_languages_step(request, steps, step, form_data)
    elif step == 9:  # Custom Sections
        return handle_custom_sections_step(request, steps, step, form_data)

    # Fallback
    return redirect('job_portal:template_selection')


def handle_personal_info_step(request, steps, step, form_data):
    """Handle the personal information step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        form = ResumeBasicInfoForm(request.POST)
        if form.is_valid():
            # Save form data to session
            form_data['personal_info'] = form.cleaned_data
            request.session['resume_form_data'] = form_data
            return redirect('job_portal:resume_wizard', step=step + 1)
    else:
        # Initialize form with saved data if available
        initial_data = form_data.get('personal_info', {})
        form = ResumeBasicInfoForm(initial=initial_data)

    context = {
        'form': form,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


def handle_summary_step(request, steps, step, form_data):
    """Handle the professional summary step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        form = ResumeSummaryForm(request.POST)
        if form.is_valid():
            # Save form data to session
            form_data['summary'] = form.cleaned_data['summary']
            request.session['resume_form_data'] = form_data
            return redirect('job_portal:resume_wizard', step=step + 1)
    else:
        # Initialize form with saved data if available
        initial_summary = form_data.get('summary', '')
        form = ResumeSummaryForm(initial={'summary': initial_summary})

    context = {
        'form': form,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


def handle_skills_step(request, steps, step, form_data):
    """Handle the skills step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        # Process skills data from the form
        skills_data = []
        skill_count = int(request.POST.get('skill_count', 0))

        for i in range(skill_count):
            if request.POST.get(f'skill_name_{i}'):
                skill = {
                    'skill_name': request.POST.get(f'skill_name_{i}'),
                    'skill_type': request.POST.get(f'skill_type_{i}'),
                    'proficiency_level': request.POST.get(f'proficiency_level_{i}'),
                }
                skills_data.append(skill)

        # Save skills data to session
        form_data['skills'] = skills_data
        request.session['resume_form_data'] = form_data
        return redirect('job_portal:resume_wizard', step=step + 1)

    # Initialize with saved data if available
    skills_data = form_data.get('skills', [])
    # if not skills_data:
    #     # Add empty skill forms if none exist
    #     skills_data = [{'skill_name': '', 'skill_type': 'technical', 'proficiency_level': 0}]

    skill_types = dict(Skill.SKILL_TYPES)

    context = {
        'skills': skills_data,
        'skill_types': skill_types,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


def handle_experience_step(request, steps, step, form_data):
    """Handle the work experience step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        print("Processing experience step POST request")  # Debug print
        # Process experience data from the form
        experience_data = []
        experience_count = int(request.POST.get('experience_count', 0))

        print(f"Experience count from form: {experience_count}")  # Debug print

        for i in range(experience_count):
            job_title = request.POST.get(f'job_title_{i}')
            print(f"Processing experience {i}, job title: {job_title}")  # Debug print

            if job_title:
                # Get bullet points for this experience
                bullet_points = []
                bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))

                print(f"Bullet count for experience {i}: {bullet_count}")  # Debug print

                for j in range(bullet_count):
                    bullet_text = request.POST.get(f'bullet_{i}_{j}')
                    if bullet_text:
                        bullet_points.append({'description': bullet_text})
                        print(f"Added bullet point {j}: {bullet_text[:30]}...")  # Debug print

                # Create experience entry with bullet points
                experience = {
                    'job_title': job_title,
                    'employer': request.POST.get(f'employer_{i}', ''),
                    'location': request.POST.get(f'location_{i}', ''),
                    'start_date': request.POST.get(f'start_date_{i}', ''),
                    'end_date': request.POST.get(f'end_date_{i}', ''),
                    'is_current': request.POST.get(f'is_current_{i}') == 'on',
                    'is_remote': request.POST.get(f'is_remote_{i}') == 'on',
                    'employment_type': request.POST.get(f'employment_type_{i}', ''),
                    'bullet_points': bullet_points,
                    'is_visible': request.POST.get(f'is_visible_{i}', 'on') == 'on',
                    'display_order': request.POST.get(f'display_order_{i}', i)
                }
                experience_data.append(experience)

        # Save experience data to session
        print(f"Saving {len(experience_data)} experiences to session")  # Debug print
        form_data['experiences'] = experience_data
        request.session['resume_form_data'] = form_data
        return redirect('job_portal:resume_wizard', step=step + 1)

    # Initialize with saved data if available
    experiences_data = form_data.get('experiences', [])
    if not experiences_data:
        # Add an empty experience form if none exist
        experiences_data = [{
            'job_title': '',
            'employer': '',
            'location': '',
            'start_date': '',
            'end_date': '',
            'is_current': False,
            'is_remote': False,
            'employment_type': '',
            'bullet_points': [{'description': ''}],
            'is_visible': True,
            'display_order': 0
        }]

    context = {
        'experiences': experiences_data,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
        'previous_step': step - 1 if step > 1 else None,
        'next_step': step + 1 if step < len(steps) else None,
    }
    return render(request, step_info['template'], context)


def handle_education_step(request, steps, step, form_data):
    """Handle the education step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        # Process education data from the form
        education_data = []
        education_count = int(request.POST.get('education_count', 0))

        for i in range(education_count):
            if request.POST.get(f'school_name_{i}'):
                education = {
                    'school_name': request.POST.get(f'school_name_{i}'),
                    'location': request.POST.get(f'location_{i}'),
                    'degree': request.POST.get(f'degree_{i}'),
                    'degree_type': request.POST.get(f'degree_type_{i}'),
                    'field_of_study': request.POST.get(f'field_of_study_{i}'),
                    'graduation_date': request.POST.get(f'graduation_date_{i}'),
                    'gpa': request.POST.get(f'gpa_{i}'),
                }
                education_data.append(education)

        # Save education data to session
        form_data['educations'] = education_data
        request.session['resume_form_data'] = form_data
        return redirect('job_portal:resume_wizard', step=step + 1)

    # Initialize with saved data if available
    educations_data = form_data.get('educations', [])
    if not educations_data:
        # Add an empty education form if none exist
        educations_data = [{
            'school_name': '',
            'location': '',
            'degree': '',
            'degree_type': 'bachelor',
            'field_of_study': '',
            'graduation_date': '',
            'gpa': '',
        }]

    degree_types = dict(Education.DEGREE_TYPES)

    context = {
        'educations': educations_data,
        'degree_types': degree_types,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


def handle_projects_step(request, steps, step, form_data):
    """Handle the projects step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        # Process project data from the form
        project_data = []
        project_count = int(request.POST.get('project_count', 0))

        for i in range(project_count):
            if request.POST.get(f'project_name_{i}'):
                # Get bullet points for this project
                bullet_points = []
                bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))

                for j in range(bullet_count):
                    bullet_text = request.POST.get(f'bullet_{i}_{j}')
                    if bullet_text:
                        bullet_points.append(bullet_text)

                # Create project entry with bullet points
                project = {
                    'project_name': request.POST.get(f'project_name_{i}'),
                    'summary': request.POST.get(f'summary_{i}'),
                    'start_date': request.POST.get(f'start_date_{i}'),
                    'completion_date': request.POST.get(f'completion_date_{i}'),
                    'project_link': request.POST.get(f'project_link_{i}'),
                    'github_link': request.POST.get(f'github_link_{i}'),
                    'bullet_points': bullet_points,
                }
                project_data.append(project)

        # Save project data to session
        form_data['projects'] = project_data
        request.session['resume_form_data'] = form_data
        return redirect('job_portal:resume_wizard', step=step + 1)

    # Initialize with saved data if available
    projects_data = form_data.get('projects', [])
    if not projects_data:
        # Add an empty project form if none exist
        projects_data = [{
            'project_name': '',
            'summary': '',
            'start_date': '',
            'completion_date': '',
            'project_link': '',
            'github_link': '',
            'bullet_points': ['', '', '']
        }]

    context = {
        'projects': projects_data,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


def handle_certifications_step(request, steps, step, form_data):
    """Handle the certifications step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        # Process certification data from the form
        certification_data = []
        certification_count = int(request.POST.get('certification_count', 0))

        for i in range(certification_count):
            if request.POST.get(f'name_{i}'):
                certification = {
                    'name': request.POST.get(f'name_{i}'),
                    'institute': request.POST.get(f'institute_{i}'),
                    'completion_date': request.POST.get(f'completion_date_{i}'),
                    'expiration_date': request.POST.get(f'expiration_date_{i}'),
                    'score': request.POST.get(f'score_{i}'),
                    'link': request.POST.get(f'link_{i}'),
                    'description': request.POST.get(f'description_{i}'),
                }
                certification_data.append(certification)

        # Save certification data to session
        form_data['certifications'] = certification_data
        request.session['resume_form_data'] = form_data
        return redirect('job_portal:resume_wizard', step=step + 1)

    # Initialize with saved data if available
    certifications_data = form_data.get('certifications', [])
    if not certifications_data:
        # Add an empty certification form if none exist
        certifications_data = [{
            'name': '',
            'institute': '',
            'completion_date': '',
            'expiration_date': '',
            'score': '',
            'link': '',
            'description': '',
        }]

    context = {
        'certifications': certifications_data,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


def handle_languages_step(request, steps, step, form_data):
    """Handle the languages step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        # Process language data from the form
        language_data = []
        language_count = int(request.POST.get('language_count', 0))

        for i in range(language_count):
            if request.POST.get(f'language_name_{i}'):
                language = {
                    'language_name': request.POST.get(f'language_name_{i}'),
                    'proficiency': request.POST.get(f'proficiency_{i}'),
                }
                language_data.append(language)

        # Save language data to session
        form_data['languages'] = language_data
        request.session['resume_form_data'] = form_data
        return redirect('job_portal:resume_wizard', step=step + 1)

    # Initialize with saved data if available
    languages_data = form_data.get('languages', [])
    if not languages_data:
        # Add an empty language form if none exist
        languages_data = [{
            'language_name': '',
            'proficiency': 'basic',
        }]

    proficiency_levels = dict(Language.PROFICIENCY_LEVELS)

    context = {
        'languages': languages_data,
        'proficiency_levels': proficiency_levels,
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


def handle_custom_sections_step(request, steps, step, form_data):
    """Handle the custom sections step of the wizard."""
    step_info = steps[step]

    if request.method == 'POST':
        # Process custom section data from the form
        custom_data = []
        section_count = int(request.POST.get('section_count', 0))

        for i in range(section_count):
            if request.POST.get(f'name_{i}'):
                section = {
                    'name': request.POST.get(f'name_{i}'),
                    'completion_date': request.POST.get(f'completion_date_{i}'),
                    'bullet_points': request.POST.get(f'bullet_points_{i}'),
                    'description': request.POST.get(f'description_{i}'),
                    'link': request.POST.get(f'link_{i}'),
                    'institution_name': request.POST.get(f'institution_name_{i}'),
                }
                custom_data.append(section)

        # Save custom section data to session
        form_data['custom_sections'] = custom_data
        request.session['resume_form_data'] = form_data

        # This is the last step, redirect to resume generation
        return redirect('job_portal:generate_resume')

    # Initialize with saved data if available
    custom_sections_data = form_data.get('custom_sections', [])
    if not custom_sections_data:
        # Add an empty custom section form if none exist
        custom_sections_data = [{
            'name': '',
            'completion_date': '',
            'bullet_points': '',
            'description': '',
            'link': '',
            'institution_name': '',
        }]

    # Add default section ideas
    default_ideas = [
        {
            "name": "Volunteer Experience",
            "description": "Highlight your community service and volunteer work",
            "icon": "fa-hands-helping"
        },
        {
            "name": "Publications",
            "description": "List articles, papers, or books you've authored",
            "icon": "fa-book"
        },
        {
            "name": "Awards & Honors",
            "description": "Showcase recognition you've received in your field",
            "icon": "fa-trophy"
        },
        {
            "name": "Professional Memberships",
            "description": "List industry associations or organizations you belong to",
            "icon": "fa-users"
        },
        {
            "name": "Conferences & Events",
            "description": "Feature events where you've presented or participated",
            "icon": "fa-microphone"
        },
        {
            "name": "Courses & Training",
            "description": "Highlight additional training beyond your formal education",
            "icon": "fa-graduation-cap"
        }
    ]

    context = {
        'custom_sections': custom_sections_data,
        'default_ideas': default_ideas,  # Add this line
        'step': step,
        'total_steps': len(steps),
        'step_title': step_info['title'],
        'template_id': request.session.get('resume_template_id'),
    }
    return render(request, step_info['template'], context)


@login_required
def generate_resume(request):
    """Generate the final resume based on all the collected data."""
    # Get resume data from session
    form_data = request.session.get('resume_form_data', {})
    template_id = request.session.get('resume_template_id')

    if not form_data or not template_id:
        messages.error(request, "Missing resume data. Please start over.")
        return redirect('job_portal:template_selection')

    try:
        with transaction.atomic():
            # Create the Resume object
            personal_info = form_data.get('personal_info', {})

            # Fix for the summary field - handle both string and dict cases
            summary = form_data.get('summary', '')

            # Check if summary is a string or dict and handle accordingly
            if isinstance(summary, dict):
                summary_text = summary.get('summary', '')
            else:
                summary_text = summary  # Use the summary string directly

            resume = Resume(
                first_name=personal_info.get('first_name', ''),
                mid_name=personal_info.get('mid_name', ''),
                last_name=personal_info.get('last_name', ''),
                email=personal_info.get('email', ''),
                phone=personal_info.get('phone', ''),
                address=personal_info.get('address', ''),
                linkedin=personal_info.get('linkedin', ''),
                github=personal_info.get('github', ''),
                portfolio=personal_info.get('portfolio', ''),
                summary=summary_text,  # Use the correctly extracted summary
                user=request.user,
                status='generated'
            )
            resume.save()

            # Process skills
            for skill_data in form_data.get('skills', []):
                Skill.objects.create(
                    resume=resume,
                    skill_name=skill_data.get('skill_name', ''),
                    skill_type=skill_data.get('skill_type', 'technical'),
                    proficiency_level=skill_data.get('proficiency_level', 0)
                )

            # Process experiences
            for exp_data in form_data.get('experiences', []):
                experience = Experience.objects.create(
                    resume=resume,
                    job_title=exp_data.get('job_title', ''),
                    employer=exp_data.get('employer', ''),
                    location=exp_data.get('location', ''),
                    start_date=exp_data.get('start_date') or None,
                    end_date=exp_data.get('end_date') or None,
                    is_current=exp_data.get('is_current', False)
                )

                # Add bullet points
                for bullet_data in exp_data.get('bullet_points', []):
                    bullet_text = bullet_data
                    # Handle both string and dict formats for bullet points
                    if isinstance(bullet_data, dict):
                        bullet_text = bullet_data.get('description', '')

                    if bullet_text:
                        ExperienceBulletPoint.objects.create(
                            experience=experience,
                            description=bullet_text
                        )

            # Process education
            for edu_data in form_data.get('educations', []):
                Education.objects.create(
                    resume=resume,
                    school_name=edu_data.get('school_name', ''),
                    location=edu_data.get('location', ''),
                    degree=edu_data.get('degree', ''),
                    degree_type=edu_data.get('degree_type', 'bachelor'),
                    field_of_study=edu_data.get('field_of_study', ''),
                    graduation_date=edu_data.get('graduation_date') or None,
                    gpa=edu_data.get('gpa') or None
                )

            # Process projects
            for proj_data in form_data.get('projects', []):
                project = Project.objects.create(
                    resume=resume,
                    project_name=proj_data.get('project_name', ''),
                    summary=proj_data.get('summary', ''),
                    start_date=proj_data.get('start_date') or None,
                    completion_date=proj_data.get('completion_date') or None,
                    project_link=proj_data.get('project_link', ''),
                    github_link=proj_data.get('github_link', '')
                )

                # Add bullet points
                for bullet_text in proj_data.get('bullet_points', []):
                    if bullet_text:
                        ProjectBulletPoint.objects.create(
                            project=project,
                            description=bullet_text
                        )

            # Process certifications
            for cert_data in form_data.get('certifications', []):
                Certification.objects.create(
                    resume=resume,
                    name=cert_data.get('name', ''),
                    institute=cert_data.get('institute', ''),
                    completion_date=cert_data.get('completion_date') or None,
                    expiration_date=cert_data.get('expiration_date') or None,
                    score=cert_data.get('score', ''),
                    link=cert_data.get('link', ''),
                    description=cert_data.get('description', '')
                )

            # Process languages
            for lang_data in form_data.get('languages', []):
                Language.objects.create(
                    resume=resume,
                    language_name=lang_data.get('language_name', ''),
                    proficiency=lang_data.get('proficiency', 'basic')
                )

            # Process custom sections
            for custom_data in form_data.get('custom_sections', []):
                if custom_data.get('name'):
                    CustomData.objects.create(
                        resume=resume,
                        name=custom_data.get('name', ''),
                        completion_date=custom_data.get('completion_date') or None,
                        bullet_points=custom_data.get('bullet_points', ''),
                        description=custom_data.get('description', ''),
                        link=custom_data.get('link', ''),
                        institution_name=custom_data.get('institution_name', '')
                    )

            # Clear session data
            request.session['resume_form_data'] = {}
            request.session['resume_template_id'] = None
            request.session['resume_wizard_step'] = None

            messages.success(request, "Resume successfully created!")

            # Redirect to view the generated resume
            return redirect('job_portal:view_resume', resume_id=resume.id)

    except Exception as e:
        messages.error(request, f"Error generating resume: {str(e)}")
        return redirect('job_portal:template_selection')


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


# @login_required
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
#         context['parent_index'] = parent_index
#         return render(request, 'resumes/partials/bullet_point_form_row.html', context)
#
#     return HttpResponse("Form type not recognized")


def preview_template(request, template_id):
    """
    Preview a resume template with comprehensive sample data that includes all model fields.
    Enhanced to support the fresh graduate template with appropriate sample data.
    """
    from django.shortcuts import render
    from django.http import HttpResponse

    # Check if we should use fresher resume data
    if template_id == 6:
        sample_resume = create_fresher_resume()
    else:
        sample_resume = create_experienced_resume()

    # For consistent template rendering, make sure the template exists
    try:
        # Render the template
        return render(request, f'resumes/templates/template{template_id}.html', {'resume': sample_resume})
    except Exception as e:
        # Return a basic error page with useful information
        error_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 30px;">
            <h1 style="color: #d32f2f;">Template Preview Error</h1>
            <p>There was a problem rendering the template:</p>
            <div style="background-color: #f8f8f8; padding: 15px; border-left: 5px solid #d32f2f; margin: 20px 0;">
                <code>{str(e)}</code>
            </div>
            <p>Please check that the template file exists at: <code>resumes/templates/template{template_id}.html</code></p>
            <p>Template ID: {template_id}</p>
        </div>
        """
        return HttpResponse(error_html)


def create_experienced_resume():
    """Create a sample resume for an experienced professional."""
    from datetime import date

    class DummyQuerySet(list):
        def exists(self):
            return len(self) > 0

        def all(self):
            return self

        def get_skill_type_display(self):
            return self.skill_type.capitalize() if hasattr(self, 'skill_type') else ""

    class DummyBulletPoint:
        def __init__(self, description):
            self.description = description
            self.keywords = DummyQuerySet()

    class DummyExperience:
        def __init__(self, job_title, employer, location, start_date, end_date=None, is_current=False):
            self.job_title = job_title
            self.employer = employer
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.is_current = is_current
            self.bullet_points = DummyQuerySet()

    class DummyEducation:
        def __init__(self, school_name, location, degree, field_of_study, degree_type, graduation_date, gpa=None,
                     start_date=None):
            self.school_name = school_name
            self.location = location
            self.degree = degree
            self.field_of_study = field_of_study
            self.degree_type = degree_type
            self.graduation_date = graduation_date
            self.start_date = start_date
            self.gpa = gpa
            self.achievements = "Dean's List: 2015-2017\nSenior Project: Advanced Machine Learning Application\nRecipient of Academic Excellence Scholarship"

    class DummySkill:
        def __init__(self, name, skill_type, proficiency_level):
            self.skill_name = name
            self.skill_type = skill_type
            self.proficiency_level = proficiency_level

        def get_skill_type_display(self):
            types = {
                'technical': 'Technical',
                'soft': 'Soft',
                'language': 'Language',
                'tool': 'Tool'
            }
            return types.get(self.skill_type, self.skill_type)

    class DummyProject:
        def __init__(self, name, summary, start_date, completion_date, project_link=None, github_link=None):
            self.project_name = name
            self.summary = summary
            self.start_date = start_date
            self.completion_date = completion_date
            self.project_link = project_link
            self.github_link = github_link
            self.bullet_points = DummyQuerySet()
            self.technologies = DummyQuerySet()

    class DummyCertification:
        def __init__(self, name, institute, completion_date, expiration_date=None, description=None, link=None,
                     score=None):
            self.name = name
            self.institute = institute
            self.completion_date = completion_date
            self.expiration_date = expiration_date
            self.description = description
            self.link = link
            self.score = score

    class DummyLanguage:
        def __init__(self, name, proficiency):
            self.language_name = name
            self.proficiency = proficiency

        def get_proficiency_display(self):
            return {"basic": "Basic", "intermediate": "Intermediate",
                    "advanced": "Advanced", "native": "Native"}[self.proficiency]

    class DummyCustomData:
        def __init__(self, name, completion_date=None, bullet_points=None, description=None, link=None,
                     institution_name=None):
            self.name = name
            self.completion_date = completion_date
            self.bullet_points = bullet_points
            self.description = description
            self.link = link
            self.institution_name = institution_name

    class DummyResume:
        def __init__(self):
            self.id = 1
            self.first_name = "Alex"
            self.mid_name = "J."
            self.last_name = "Morgan"
            self.full_name = "Alex J. Morgan"
            self.title = "Senior Full Stack Developer"
            self.email = "alex.morgan@example.com"
            self.phone = "(555) 123-4567"
            self.address = "123 Tech Avenue, Silicon Valley, CA 94123"
            self.linkedin = "https://linkedin.com/in/alexmorgan"
            self.github = "https://github.com/alexmorgan"
            self.portfolio = "https://alexmorgan.dev"
            self.summary = "Innovative full stack developer with 7+ years of experience building scalable web applications and leading development teams. Specialized in JavaScript, Python, and cloud technologies with a focus on performance optimization and user experience. Passionate about creating elegant solutions to complex problems and implementing best practices in software development."

            # Initialize collections as DummyQuerySet
            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.skills = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_data = DummyQuerySet()

    # Create a sample resume
    sample_resume = DummyResume()

    # Add experiences with more variety
    experiences = [
        DummyExperience(
            "Senior Software Engineer",
            "Tech Innovations Inc.",
            "San Francisco, CA",
            date(2020, 6, 1),
            None,  # end_date
            True  # is_current
        ),
        DummyExperience(
            "Lead Developer",
            "Digital Solutions Ltd.",
            "Seattle, WA",
            date(2018, 3, 1),
            date(2020, 5, 31),
            False
        ),
        DummyExperience(
            "Web Developer",
            "Creative Web Agency",
            "Portland, OR",
            date(2016, 1, 15),
            date(2018, 2, 28),
            False
        ),
    ]

    # Add bullet points to each experience
    experiences[0].bullet_points.extend([
        DummyBulletPoint(
            "Led a team of 7 developers to deliver a cloud-based enterprise solution that increased customer engagement by 45% and reduced operational costs by 30%"),
        DummyBulletPoint(
            "Implemented microservices architecture with Docker and Kubernetes that reduced deployment time by 60% and improved system scalability"),
        DummyBulletPoint(
            "Optimized database queries and implemented caching strategies resulting in a 40% improvement in application response time"),
        DummyBulletPoint(
            "Mentored junior developers through code reviews and pair programming sessions, improving team productivity by 25%")
    ])

    experiences[1].bullet_points.extend([
        DummyBulletPoint(
            "Designed and developed a customer portal using React and Node.js that increased user satisfaction by 35%"),
        DummyBulletPoint(
            "Implemented CI/CD pipelines with Jenkins, reducing integration issues by 50% and deployment failures by 70%"),
        DummyBulletPoint(
            "Led the migration from monolithic architecture to microservices, improving system reliability and reducing downtime by 80%")
    ])

    experiences[2].bullet_points.extend([
        DummyBulletPoint(
            "Developed responsive web applications using JavaScript, HTML5, and CSS3 for clients across various industries"),
        DummyBulletPoint("Integrated third-party APIs to enhance application functionality and user experience"),
        DummyBulletPoint("Collaborated with UX/UI designers to implement intuitive and accessible user interfaces")
    ])

    sample_resume.experiences.extend(experiences)

    # Add education with complete details
    educations = [
        DummyEducation(
            "University of Technology",
            "Boston, MA",
            "Master of Science",
            "Computer Science",
            "master",
            date(2016, 5, 15),
            3.92,
            date(2014, 9, 1)
        ),
        DummyEducation(
            "State University",
            "Los Angeles, CA",
            "Bachelor of Science",
            "Software Engineering",
            "bachelor",
            date(2014, 6, 15),
            3.8,
            date(2010, 9, 1)
        )
    ]
    sample_resume.educations.extend(educations)

    # Add skills with all skill types
    skills = [
        # Technical skills
        DummySkill("JavaScript", "technical", 95),
        DummySkill("Python", "language", 90),
        DummySkill("React", "language", 85),
        DummySkill("Node.js", "language", 85),
        DummySkill("TypeScript", "language", 80),
        DummySkill("Django", "technical", 80),
        DummySkill("RESTful APIs", "technical", 90),
        DummySkill("GraphQL", "technical", 75),
        DummySkill("PostgreSQL", "technical", 85),
        DummySkill("MongoDB", "technical", 80),

        # Tools
        DummySkill("AWS", "tool", 85),
        DummySkill("Docker", "tool", 80),
        DummySkill("Kubernetes", "tool", 75),
        DummySkill("Git", "tool", 90),
        DummySkill("Jenkins", "tool", 80),
        DummySkill("JIRA", "tool", 85),

        # Soft skills
        DummySkill("Team Leadership", "soft", 90),
        DummySkill("Project Management", "soft", 85),
        DummySkill("Communication", "soft", 95),
        DummySkill("Problem Solving", "soft", 90),
        DummySkill("Agile Methodologies", "soft", 85)
    ]
    sample_resume.skills.extend(skills)

    # Add projects with technologies
    projects = [
        DummyProject(
            "E-commerce Analytics Dashboard",
            "A responsive web application that visualizes sales data and customer insights for online retailers",
            date(2022, 3, 1),
            date(2022, 8, 15),
            "https://dashboard-demo.example.com",
            "https://github.com/example/analytics-dashboard"
        ),
        DummyProject(
            "Content Management System",
            "A customizable CMS with advanced user permissions and real-time collaboration features",
            date(2021, 5, 1),
            date(2021, 12, 10),
            "https://cms-example.com",
            "https://github.com/example/modern-cms"
        )
    ]

    # Add bullet points to projects
    projects[0].bullet_points.extend([
        DummyBulletPoint(
            "Designed and implemented interactive data visualizations using D3.js and React, providing actionable insights on sales trends"),
        DummyBulletPoint(
            "Integrated with RESTful APIs to fetch real-time sales and inventory data from multiple sources"),
        DummyBulletPoint("Implemented user authentication and role-based access control to ensure data security"),
        DummyBulletPoint("Created a responsive design that works seamlessly across desktop and mobile devices")
    ])

    projects[1].bullet_points.extend([
        DummyBulletPoint("Developed a plugin-based architecture allowing for easy extension of core functionality"),
        DummyBulletPoint("Implemented real-time collaboration features using WebSockets and Redis"),
        DummyBulletPoint("Created a customizable workflow engine to support complex content approval processes"),
        DummyBulletPoint("Optimized performance using lazy loading and efficient caching strategies")
    ])

    # Add technologies to projects
    tech_map = {
        "React": "technical",
        "Node.js": "technical",
        "MongoDB": "technical",
        "Express.js": "technical",
        "D3.js": "technical",
        "Redis": "technical",
        "AWS S3": "tool",
        "Docker": "tool"
    }

    for tech_name, tech_type in list(tech_map.items())[:4]:  # First 4 for project 1
        projects[0].technologies.append(DummySkill(tech_name, tech_type, 85))

    for tech_name, tech_type in list(tech_map.items())[4:]:  # Last 4 for project 2
        projects[1].technologies.append(DummySkill(tech_name, tech_type, 85))

    sample_resume.projects.extend(projects)

    # Add certifications with all fields
    certifications = [
        DummyCertification(
            "AWS Certified Solutions Architect - Professional",
            "Amazon Web Services",
            date(2022, 4, 10),
            date(2025, 4, 10),
            "Professional certification validating expertise in designing distributed systems on AWS",
            "https://aws.amazon.com/certification/certified-solutions-architect-professional/",
            "950/1000"
        ),
        DummyCertification(
            "Certified Kubernetes Administrator",
            "Cloud Native Computing Foundation",
            date(2021, 8, 15),
            date(2024, 8, 15),
            "Certification for Kubernetes administration and deployment expertise",
            "https://www.cncf.io/certification/cka/",
            "92%"
        )
    ]
    sample_resume.certifications.extend(certifications)

    # Add languages
    languages = [
        DummyLanguage("English", "native"),
        DummyLanguage("Spanish", "advanced"),
        DummyLanguage("French", "intermediate"),
        DummyLanguage("Mandarin", "basic")
    ]
    sample_resume.languages.extend(languages)

    # Add custom data sections
    custom_data_sections = [
        DummyCustomData(
            "Volunteer Experience",
            date(2022, 8, 1),
            "Developed a donation tracking system for a local food bank\nCreated a volunteer management application for disaster relief coordination\nMentored high school students in programming basics through weekly workshops",
            "Volunteered with Code for Good to develop web applications for non-profit organizations",
            "https://codeforgood.example.org",
            "Code for Good"
        ),
        DummyCustomData(
            "Publications",
            date(2021, 3, 15),
            "Published 'Scalable Architecture Patterns for Modern Web Applications' in Journal of Software Engineering\nContributed to 'Best Practices in Microservices Design' technical white paper\nAuthored multiple technical blog posts on Medium's Better Programming publication",
            "Technical publications related to software architecture and development",
            "https://medium.com/@alexmorgan",
            "Various Publishers"
        ),
        DummyCustomData(
            "Awards & Recognition",
            date(2021, 11, 10),
            "Developer of the Year, Company Awards 2021\nHackathon Winner, Healthcare Innovation Challenge 2020\nRecognized for Outstanding Technical Leadership, Q3 2019",
            "Professional recognition and awards received throughout career"
        )
    ]
    sample_resume.custom_data.extend(custom_data_sections)

    # Modify DummyQuerySet to support template regroup tag
    sample_resume.skills.get_skill_type_display = lambda: 'Technical'

    return sample_resume


def create_fresher_resume():
    """Create a sample resume for a fresh graduate with appropriate data."""
    from datetime import date

    class DummyQuerySet(list):
        def exists(self):
            return len(self) > 0

        def all(self):
            return self

        def get_skill_type_display(self):
            return self.skill_type.capitalize() if hasattr(self, 'skill_type') else ""

    class DummyBulletPoint:
        def __init__(self, description):
            self.description = description
            self.keywords = DummyQuerySet()

    class DummyExperience:
        def __init__(self, job_title, employer, location, start_date, end_date=None, is_current=False):
            self.job_title = job_title
            self.employer = employer
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.is_current = is_current
            self.bullet_points = DummyQuerySet()

    class DummyEducation:
        def __init__(self, school_name, location, degree, field_of_study, degree_type, graduation_date, gpa=None,
                     start_date=None):
            self.school_name = school_name
            self.location = location
            self.degree = degree
            self.field_of_study = field_of_study
            self.degree_type = degree_type
            self.graduation_date = graduation_date
            self.start_date = start_date
            self.gpa = gpa
            self.achievements = "Dean's List: 2022-2023\nCompleted final project with highest honors\nSelected for prestigious internship program\nWon 2nd place in university hackathon"

    class DummySkill:
        def __init__(self, name, skill_type, proficiency_level):
            self.skill_name = name
            self.skill_type = skill_type
            self.proficiency_level = proficiency_level

        def get_skill_type_display(self):
            types = {
                'technical': 'Technical',
                'soft': 'Soft',
                'language': 'Language',
                'tool': 'Tool'
            }
            return types.get(self.skill_type, self.skill_type)

    class DummyProject:
        def __init__(self, name, summary, start_date, completion_date, project_link=None, github_link=None):
            self.project_name = name
            self.summary = summary
            self.start_date = start_date
            self.completion_date = completion_date
            self.project_link = project_link
            self.github_link = github_link
            self.bullet_points = DummyQuerySet()
            self.technologies = DummyQuerySet()

    class DummyCertification:
        def __init__(self, name, institute, completion_date, expiration_date=None, description=None, link=None,
                     score=None):
            self.name = name
            self.institute = institute
            self.completion_date = completion_date
            self.expiration_date = expiration_date
            self.description = description
            self.link = link
            self.score = score

    class DummyLanguage:
        def __init__(self, name, proficiency):
            self.language_name = name
            self.proficiency = proficiency

        def get_proficiency_display(self):
            return {"basic": "Basic", "intermediate": "Intermediate",
                    "advanced": "Advanced", "native": "Native"}[self.proficiency]

    class DummyCustomData:
        def __init__(self, name, completion_date=None, bullet_points=None, description=None, link=None,
                     institution_name=None):
            self.name = name
            self.completion_date = completion_date
            self.bullet_points = bullet_points
            self.description = description
            self.link = link
            self.institution_name = institution_name

    class DummyResume:
        def __init__(self):
            self.id = 1
            self.first_name = "Jamie"
            self.mid_name = ""
            self.last_name = "Taylor"
            self.full_name = "Jamie Taylor"
            self.title = "Computer Science Graduate"
            self.email = "jamie.taylor@example.com"
            self.phone = "(555) 987-6543"
            self.address = "123 University Ave, Boston, MA 02215"
            self.linkedin = "https://linkedin.com/in/jamietaylor"
            self.github = "https://github.com/jamietaylor"
            self.portfolio = "https://jamietaylor.dev"
            self.summary = "Recent Computer Science graduate with strong foundations in programming, algorithms, and web development. Completed multiple projects showcasing skills in Python, Java, and JavaScript. Eager to apply academic knowledge and technical abilities in a professional software development role to build innovative and efficient solutions."

            # Initialize collections
            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.skills = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_data = DummyQuerySet()

    # Create fresh graduate resume
    fresher_resume = DummyResume()

    # Add education (primary focus for a fresher resume)
    education = DummyEducation(
        "Boston University",
        "Boston, MA",
        "Bachelor of Science",
        "Computer Science",
        "bachelor",
        date(2023, 5, 15),  # Recent graduation
        3.8,
        date(2019, 9, 1)
    )
    fresher_resume.educations.append(education)

    # Add internship experience (limited experience for a fresher)
    internship = DummyExperience(
        "Software Development Intern",
        "TechStart Solutions",
        "Boston, MA",
        date(2022, 6, 1),
        date(2022, 8, 31),
        False
    )
    internship.bullet_points.extend([
        DummyBulletPoint(
            "Assisted in developing and testing features for the company's e-commerce platform using React and Node.js"),
        DummyBulletPoint(
            "Participated in daily scrum meetings and collaborated with senior developers on code reviews"),
        DummyBulletPoint("Implemented responsive design improvements that enhanced mobile user experience by 25%")
    ])
    fresher_resume.experiences.append(internship)

    # Add part-time job during studies
    part_time = DummyExperience(
        "Computer Lab Assistant",
        "Boston University IT Department",
        "Boston, MA",
        date(2021, 9, 1),
        date(2023, 5, 15),
        False
    )
    part_time.bullet_points.extend([
        DummyBulletPoint("Provided technical support to students and faculty for hardware and software issues"),
        DummyBulletPoint("Maintained computer lab equipment and assisted in software installations and updates"),
        DummyBulletPoint("Conducted basic programming tutoring sessions for introductory CS courses")
    ])
    fresher_resume.experiences.append(part_time)

    # Add projects (important for freshers to showcase skills)
    project1 = DummyProject(
        "Student Management System",
        "A full-stack web application for managing student records, courses, and grades",
        date(2022, 9, 1),
        date(2023, 4, 30),
        "https://student-ms-demo.example.com",
        "https://github.com/jamietaylor/student-ms"
    )
    project1.bullet_points.extend([
        DummyBulletPoint(
            "Designed and implemented a database schema with MySQL to store student and course information"),
        DummyBulletPoint(
            "Developed a responsive front-end using React and Bootstrap that allows for intuitive navigation"),
        DummyBulletPoint(
            "Implemented secure user authentication with different permission levels for students and administrators")
    ])
    project1.technologies.extend([
        DummySkill("React", "technical", 80),
        DummySkill("Node.js", "technical", 75),
        DummySkill("MySQL", "technical", 85),
        DummySkill("Bootstrap", "technical", 90)
    ])

    project2 = DummyProject(
        "Weather Forecast Mobile App",
        "A cross-platform mobile application showing detailed weather forecasts and alerts",
        date(2021, 11, 1),
        date(2022, 2, 28),
        "https://weather-app-demo.example.com",
        "https://github.com/jamietaylor/weather-app"
    )
    project2.bullet_points.extend([
        DummyBulletPoint("Created a cross-platform mobile app using Flutter that fetches and displays weather data"),
        DummyBulletPoint("Integrated with OpenWeatherMap API to retrieve real-time weather information"),
        DummyBulletPoint("Implemented location-based services to automatically detect the user's current location")
    ])
    project2.technologies.extend([
        DummySkill("Flutter", "technical", 75),
        DummySkill("Dart", "language", 70),
        DummySkill("REST APIs", "technical", 80),
        DummySkill("Firebase", "tool", 65)
    ])



    fresher_resume.projects.extend([project1, project2])

    # Add skills (focus on skills relevant for entry-level positions)
    skills = [
        # Programming languages
        DummySkill("Java", "language", 85),
        DummySkill("Python", "language", 90),
        DummySkill("JavaScript", "language", 80),
        DummySkill("HTML/CSS", "language", 85),
        DummySkill("SQL", "language", 75),
        DummySkill("C++", "language", 70),

        # Technical skills
        DummySkill("Data Structures", "technical", 85),
        DummySkill("Algorithms", "technical", 80),
        DummySkill("Object-Oriented Programming", "technical", 85),
        DummySkill("Web Development", "technical", 80),
        DummySkill("Mobile Development", "technical", 75),
        DummySkill("Database Design", "technical", 70),

        # Tools and frameworks
        DummySkill("Git", "tool", 85),
        DummySkill("React", "tool", 75),
        DummySkill("Node.js", "tool", 70),
        DummySkill("Flutter", "tool", 65),
        DummySkill("Docker", "tool", 60),
        DummySkill("VS Code", "tool", 90),

        # Soft skills
        DummySkill("Problem Solving", "soft", 85),
        DummySkill("Teamwork", "soft", 90),
        DummySkill("Communication", "soft", 85),
        DummySkill("Time Management", "soft", 80),
        DummySkill("Adaptability", "soft", 85)
    ]
    fresher_resume.skills.extend(skills)

    # Add certifications (entry-level certifications)
    certifications = [
        DummyCertification(
            "AWS Certified Cloud Practitioner",
            "Amazon Web Services",
            date(2023, 1, 15),
            date(2026, 1, 15),
            "Foundational certification validating understanding of AWS Cloud",
            "https://aws.amazon.com/certification/certified-cloud-practitioner/",
            "820/1000"
        ),
        DummyCertification(
            "Oracle Certified Associate Java Programmer",
            "Oracle",
            date(2022, 6, 10),
            None,
            "Entry-level certification for Java programming language",
            "https://education.oracle.com/java-certification-path",
            "85%"
        ),
        DummyCertification(
            "Microsoft Certified: Azure Fundamentals",
            "Microsoft",
            date(2022, 11, 20),
            None,
            "Basic understanding of cloud services and Microsoft Azure",
            "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/",
            "875/1000"
        )
    ]
    fresher_resume.certifications.extend(certifications)

    # Add languages
    languages = [
        DummyLanguage("English", "native"),
        DummyLanguage("Spanish", "intermediate"),
        DummyLanguage("French", "basic")
    ]
    fresher_resume.languages.extend(languages)

    # Add extracurricular activities and achievements (important for freshers)
    custom_data_sections = [
        DummyCustomData(
            "Extracurricular Activities",
            date(2023, 5, 1),
            "Member of the University Coding Club (2021-2023)\nParticipated in three Hackathons, winning 2nd place in CodeJam 2022\nVolunteered as a peer mentor for first-year Computer Science students\nContributed to open-source projects on GitHub",
            "Active participation in university and community technical activities",
            None,
            "Boston University"
        ),

    ]
    fresher_resume.custom_data.extend(custom_data_sections)

    # Modify DummyQuerySet to support template regroup tag
    fresher_resume.skills.get_skill_type_display = lambda: 'Technical'

    return fresher_resume


@login_required
@require_http_methods(["GET", "POST"])
def preview_current_resume(request):
    """
    Generate a live preview of the resume with all available data from session and current form.
    This view merges data from previous steps stored in the session with the current form data.
    """
    # Get template ID from session
    template_id = request.session.get('resume_template_id')
    if not template_id:
        return HttpResponse("<div class='p-4 text-center text-red-500'>Please select a template first.</div>")

    # Get ALL stored form data from session - this is crucial to get data from previous steps
    form_data = request.session.get('resume_form_data', {})

    # If this is a POST request, merge current form data without overwriting saved data
    if request.method == 'POST':
        # Save current form data to the relevant section in form_data
        current_step = request.session.get('resume_wizard_step', 1)

        if current_step == 1:  # Personal info
            personal_info = {}
            for key in ['first_name', 'mid_name', 'last_name', 'email', 'phone', 'address',
                        'linkedin', 'github', 'portfolio']:
                if key in request.POST:
                    personal_info[key] = request.POST.get(key)

            if personal_info:
                form_data['personal_info'] = personal_info

        elif current_step == 2:  # Summary
            if 'summary' in request.POST:
                form_data['summary'] = request.POST.get('summary')

        elif current_step == 3:  # Skills
            # Process skills data from the form
            skills_data = []
            skill_count = int(request.POST.get('skill_count', 0))

            for i in range(skill_count):
                if request.POST.get(f'skill_name_{i}'):
                    skill = {
                        'skill_name': request.POST.get(f'skill_name_{i}'),
                        'skill_type': request.POST.get(f'skill_type_{i}'),
                        'proficiency_level': request.POST.get(f'proficiency_level_{i}'),
                    }
                    skills_data.append(skill)

            # Save skills data to session
            if skills_data:
                form_data['skills'] = skills_data

        elif current_step == 4:  # Work Experience
            # Process experience data from the form
            experience_data = []
            experience_count = int(request.POST.get('experience_count', 0))

            for i in range(experience_count):
                if request.POST.get(f'job_title_{i}'):
                    # Get bullet points for this experience
                    bullet_points = []
                    bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))

                    for j in range(bullet_count):
                        bullet_text = request.POST.get(f'bullet_{i}_{j}')
                        if bullet_text:
                            bullet_points.append(bullet_text)

                    # Create experience entry with bullet points
                    experience = {
                        'job_title': request.POST.get(f'job_title_{i}'),
                        'employer': request.POST.get(f'employer_{i}'),
                        'location': request.POST.get(f'location_{i}'),
                        'start_date': request.POST.get(f'start_date_{i}'),
                        'end_date': request.POST.get(f'end_date_{i}'),
                        'is_current': request.POST.get(f'is_current_{i}') == 'on',
                        'bullet_points': bullet_points
                    }
                    experience_data.append(experience)

            # Save experience data to session
            if experience_data:
                form_data['experiences'] = experience_data

        elif current_step == 5:  # Education
            # Process education data from the form
            education_data = []
            education_count = int(request.POST.get('education_count', 0))

            for i in range(education_count):
                if request.POST.get(f'school_name_{i}'):
                    education = {
                        'school_name': request.POST.get(f'school_name_{i}'),
                        'location': request.POST.get(f'location_{i}'),
                        'degree': request.POST.get(f'degree_{i}'),
                        'degree_type': request.POST.get(f'degree_type_{i}'),
                        'field_of_study': request.POST.get(f'field_of_study_{i}'),
                        'graduation_date': request.POST.get(f'graduation_date_{i}'),
                        'gpa': request.POST.get(f'gpa_{i}'),
                    }
                    education_data.append(education)

            # Save education data to session
            if education_data:
                form_data['educations'] = education_data

        elif current_step == 6:  # Projects
            # Process project data from the form
            project_data = []
            project_count = int(request.POST.get('project_count', 0))

            for i in range(project_count):
                if request.POST.get(f'project_name_{i}'):
                    # Get bullet points for this project
                    bullet_points = []
                    bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))

                    for j in range(bullet_count):
                        bullet_text = request.POST.get(f'bullet_{i}_{j}')
                        if bullet_text:
                            bullet_points.append(bullet_text)

                    # Create project entry with bullet points
                    project = {
                        'project_name': request.POST.get(f'project_name_{i}'),
                        'summary': request.POST.get(f'summary_{i}'),
                        'start_date': request.POST.get(f'start_date_{i}'),
                        'completion_date': request.POST.get(f'completion_date_{i}'),
                        'project_link': request.POST.get(f'project_link_{i}'),
                        'github_link': request.POST.get(f'github_link_{i}'),
                        'bullet_points': bullet_points,
                    }
                    project_data.append(project)

            # Save project data to session
            if project_data:
                form_data['projects'] = project_data

        elif current_step == 7:  # Certifications
            # Process certification data from the form
            certification_data = []
            certification_count = int(request.POST.get('certification_count', 0))

            for i in range(certification_count):
                if request.POST.get(f'name_{i}'):
                    certification = {
                        'name': request.POST.get(f'name_{i}'),
                        'institute': request.POST.get(f'institute_{i}'),
                        'completion_date': request.POST.get(f'completion_date_{i}'),
                        'expiration_date': request.POST.get(f'expiration_date_{i}'),
                        'score': request.POST.get(f'score_{i}'),
                        'link': request.POST.get(f'link_{i}'),
                        'description': request.POST.get(f'description_{i}'),
                    }
                    certification_data.append(certification)

            # Save certification data to session
            if certification_data:
                form_data['certifications'] = certification_data

        elif current_step == 8:  # Languages
            # Process language data from the form
            language_data = []
            language_count = int(request.POST.get('language_count', 0))

            for i in range(language_count):
                if request.POST.get(f'language_name_{i}'):
                    language = {
                        'language_name': request.POST.get(f'language_name_{i}'),
                        'proficiency': request.POST.get(f'proficiency_{i}'),
                    }
                    language_data.append(language)

            # Save language data to session
            if language_data:
                form_data['languages'] = language_data

        elif current_step == 9:  # Custom Sections
            # Process custom section data from the form
            custom_data = []
            section_count = int(request.POST.get('section_count', 0))

            for i in range(section_count):
                if request.POST.get(f'name_{i}'):
                    section = {
                        'name': request.POST.get(f'name_{i}'),
                        'completion_date': request.POST.get(f'completion_date_{i}'),
                        'bullet_points': request.POST.get(f'bullet_points_{i}'),
                        'description': request.POST.get(f'description_{i}'),
                        'link': request.POST.get(f'link_{i}'),
                        'institution_name': request.POST.get(f'institution_name_{i}'),
                    }
                    custom_data.append(section)

            # Save custom section data to session
            if custom_data:
                form_data['custom_sections'] = custom_data

    # Create a dummy resume object for the template that mimics your model structure
    class DummyQuerySet(list):
        def exists(self):
            return len(self) > 0

        def all(self):
            return self

    class DummyBulletPoint:
        def __init__(self, description):
            self.description = description

    class DummySkill:
        def __init__(self, data):
            self.skill_name = data.get('skill_name', '')
            self.skill_type = data.get('skill_type', 'technical')
            self.proficiency_level = data.get('proficiency_level', 0)

        def get_skill_type_display(self):
            types = {
                'technical': 'Technical',
                'soft': 'Soft',
                'language': 'Language',
                'tool': 'Tool'
            }
            return types.get(self.skill_type, self.skill_type)

    class DummyExperience:
        def __init__(self, data):
            from datetime import datetime

            self.job_title = data.get('job_title', '')
            self.employer = data.get('employer', '')
            self.location = data.get('location', '')

            # Process start date
            start_date_str = data.get('start_date', '')
            if start_date_str:
                try:
                    date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    self.start_date = date_obj
                except (ValueError, TypeError):
                    self.start_date = start_date_str
            else:
                self.start_date = None

            # Handle is_current flag
            self.is_current = data.get('is_current', False)
            if isinstance(self.is_current, str):
                self.is_current = self.is_current.lower() in ['on', 'true', '1', 'yes']

            # Process end date
            end_date_str = data.get('end_date', '')
            if end_date_str and not self.is_current:
                try:
                    date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    self.end_date = date_obj
                except (ValueError, TypeError):
                    self.end_date = end_date_str
            else:
                self.end_date = None

            # Create formatted dates for display
            self.formatted_start_date = self._format_date(self.start_date)
            self.formatted_end_date = 'Present' if self.is_current else self._format_date(self.end_date)

            # Create a formatted date range string
            if self.formatted_start_date:
                if self.is_current:
                    self.date_range = f"{self.formatted_start_date} - Present"
                elif self.formatted_end_date:
                    self.date_range = f"{self.formatted_start_date} - {self.formatted_end_date}"
                else:
                    self.date_range = self.formatted_start_date
            else:
                self.date_range = ""

            # Add bullet points
            self.bullet_points = DummyQuerySet()
            for bp_text in data.get('bullet_points', []):
                self.bullet_points.append(DummyBulletPoint(bp_text))

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyEducation:
        def __init__(self, data):
            from datetime import datetime

            self.school_name = data.get('school_name', '')
            self.location = data.get('location', '')
            self.degree = data.get('degree', '')
            self.degree_type = data.get('degree_type', 'bachelor')
            self.field_of_study = data.get('field_of_study', '')

            # Process graduation date
            grad_date_str = data.get('graduation_date', '')
            if grad_date_str:
                try:
                    date_obj = datetime.strptime(grad_date_str, '%Y-%m-%d').date()
                    self.graduation_date = date_obj
                except (ValueError, TypeError):
                    self.graduation_date = grad_date_str
            else:
                self.graduation_date = None

            self.formatted_graduation_date = self._format_date(self.graduation_date)
            self.gpa = data.get('gpa', '')

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyProject:
        def __init__(self, data):
            from datetime import datetime

            self.project_name = data.get('project_name', '')
            self.summary = data.get('summary', '')

            # Process start date
            start_date_str = data.get('start_date', '')
            if start_date_str:
                try:
                    date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    self.start_date = date_obj
                except (ValueError, TypeError):
                    self.start_date = start_date_str
            else:
                self.start_date = None

            # Process completion date
            completion_date_str = data.get('completion_date', '')
            if completion_date_str:
                try:
                    date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                    self.completion_date = date_obj
                except (ValueError, TypeError):
                    self.completion_date = completion_date_str
            else:
                self.completion_date = None

            # Create formatted dates
            self.formatted_start_date = self._format_date(self.start_date)
            self.formatted_completion_date = self._format_date(self.completion_date)

            # Create a date range string
            if self.formatted_start_date and self.formatted_completion_date:
                self.date_range = f"{self.formatted_start_date} - {self.formatted_completion_date}"
            elif self.formatted_start_date:
                self.date_range = f"{self.formatted_start_date} - Present"
            else:
                self.date_range = ""

            self.project_link = data.get('project_link', '')
            self.github_link = data.get('github_link', '')
            self.bullet_points = DummyQuerySet()

            # Add bullet points
            for bp_text in data.get('bullet_points', []):
                self.bullet_points.append(DummyBulletPoint(bp_text))

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyCertification:
        def __init__(self, data):
            from datetime import datetime

            self.name = data.get('name', '')
            self.institute = data.get('institute', '')

            # Process completion date
            completion_date_str = data.get('completion_date', '')
            if completion_date_str:
                try:
                    date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                    self.completion_date = date_obj
                except (ValueError, TypeError):
                    self.completion_date = completion_date_str
            else:
                self.completion_date = None

            # Process expiration date
            expiration_date_str = data.get('expiration_date', '')
            if expiration_date_str:
                try:
                    date_obj = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                    self.expiration_date = date_obj
                except (ValueError, TypeError):
                    self.expiration_date = expiration_date_str
            else:
                self.expiration_date = None

            # Create formatted dates
            self.formatted_completion_date = self._format_date(self.completion_date)
            self.formatted_expiration_date = self._format_date(self.expiration_date)

            self.score = data.get('score', '')
            self.link = data.get('link', '')
            self.description = data.get('description', '')

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyLanguage:
        def __init__(self, data):
            self.language_name = data.get('language_name', '')
            self.proficiency = data.get('proficiency', 'basic')

        def get_proficiency_display(self):
            levels = {
                'basic': 'Basic',
                'intermediate': 'Intermediate',
                'advanced': 'Advanced',
                'native': 'Native'
            }
            return levels.get(self.proficiency, self.proficiency)

    class DummyCustomData:
        def __init__(self, data):
            from datetime import datetime

            self.name = data.get('name', '')

            # Process completion date
            completion_date_str = data.get('completion_date', '')
            if completion_date_str:
                try:
                    date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                    self.completion_date = date_obj
                except (ValueError, TypeError):
                    self.completion_date = completion_date_str
            else:
                self.completion_date = None

            # Create formatted date
            self.formatted_completion_date = self._format_date(self.completion_date)

            self.bullet_points = data.get('bullet_points', '')
            self.description = data.get('description', '')
            self.link = data.get('link', '')
            self.institution_name = data.get('institution_name', '')

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyResume:
        def __init__(self):
            # Add personal info attributes
            personal_info = form_data.get('personal_info', {})
            self.first_name = personal_info.get('first_name', '')
            self.mid_name = personal_info.get('mid_name', '')
            self.last_name = personal_info.get('last_name', '')
            self.full_name = f"{self.first_name} {self.mid_name} {self.last_name}".strip()
            self.email = personal_info.get('email', '')
            self.phone = personal_info.get('phone', '')
            self.address = personal_info.get('address', '')
            self.linkedin = personal_info.get('linkedin', '')
            self.github = personal_info.get('github', '')
            self.portfolio = personal_info.get('portfolio', '')

            # Add summary
            self.summary = form_data.get('summary', '')

            # Initialize collections
            self.skills = DummyQuerySet()
            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_data = DummyQuerySet()

            # Populate skills
            for skill_data in form_data.get('skills', []):
                self.skills.append(DummySkill(skill_data))

            # Populate experiences
            for exp_data in form_data.get('experiences', []):
                self.experiences.append(DummyExperience(exp_data))

            # Populate educations
            for edu_data in form_data.get('educations', []):
                self.educations.append(DummyEducation(edu_data))

            # Populate projects
            for proj_data in form_data.get('projects', []):
                self.projects.append(DummyProject(proj_data))

            # Populate certifications
            for cert_data in form_data.get('certifications', []):
                self.certifications.append(DummyCertification(cert_data))

            # Populate languages
            for lang_data in form_data.get('languages', []):
                self.languages.append(DummyLanguage(lang_data))

            # Populate custom data
            for custom_data in form_data.get('custom_sections', []):
                self.custom_data.append(DummyCustomData(custom_data))

    resume = DummyResume()

    try:
        # Use a more reliable template path that matches your project structure
        return render(request, f'resumes/templates/template{template_id}.html', {
            'resume': resume,
            'is_preview': True
        })
    except Exception as e:
        # Return error message
        error_html = f"""
        <div class="p-4 text-center">
            <h4 class="text-red-500 font-bold mb-2">Error Rendering Template</h4>
            <p class="text-gray-600 mb-2">There was a problem generating your resume preview:</p>
            <div class="bg-gray-100 p-3 rounded text-left text-sm text-gray-700 mb-4">
                <code>{str(e)}</code>
            </div>
            <p class="text-sm text-gray-500">Template path attempted: resumes/templates/template{template_id}.html</p>
        </div>
        """
        return HttpResponse(error_html)


def get_language_template(request):
    """
    Returns the HTML template for a new language form row
    """
    # Get the index from the request (defaulting to 0 if not provided)
    index = request.GET.get('index', 0)

    # Define proficiency levels for the dropdown
    proficiency_levels = {
        'native': 'Native/Fluent',
        'advanced': 'Advanced/Professional',
        'intermediate': 'Intermediate',
        'basic': 'Basic/Elementary'
    }

    # Render the language form template
    return render(request, 'resumes/partials/language_form_row.html', {
        'index': index,
        'proficiency_levels': proficiency_levels,
        'forloop': {'counter0': index, 'counter': int(index) + 1}  # Simulate forloop context for the template
    })


# views.py
import time
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.utils import timezone




@login_required
@require_http_methods(["GET"])
def ai_generate_bullets(request):
    """
    Generate bullet points based on job information using either ChatGPT or Gemini.
    This is an HTMX endpoint that returns HTML for the bullet points.
    """
    job_title = request.GET.get('job_title')
    employer = request.GET.get('employer')
    parent_index = request.GET.get('parent_index', '0')
    ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Default to ChatGPT

    # Enhanced parameters
    target_job_title = request.GET.get('target_job_title')
    skills = request.GET.get('skills')
    responsibilities = request.GET.get('responsibilities')

    # New parameter for number of bullet points requested
    bullet_count = int(request.GET.get('bullet_count', 3))
    # Ensure the count is between 1 and 5
    bullet_count = min(max(bullet_count, 1), 5)

    if not job_title or not employer:
        return HttpResponse("Job title and employer are required", status=400)

    # Start timing for API response
    start_time = time.time()

    # Choose AI engine based on user selection
    if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
        bullets, input_tokens, output_tokens = generate_bullets_chatgpt(
            job_title,
            employer,
            target_job_title,
            skills,
            responsibilities,
            bullet_count  # Pass the bullet count to the AI function
        )
    elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
        bullets, input_tokens, output_tokens = generate_bullets_gemini(
            job_title,
            employer,
            target_job_title,
            skills,
            responsibilities,
            bullet_count  # Pass the bullet count to the AI function
        )
    else:
        # Fallback to template-based generation with specified count
        bullets = get_template_bullets(job_title, employer, bullet_count)
        input_tokens = output_tokens = 0

    # Calculate API response time
    response_time = time.time() - start_time

    # Log API usage if using AI
    if (ai_engine == 'chatgpt' and settings.OPENAI_API_KEY) or (
            ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY):
        try:
            # Create API usage record
            usage = APIUsage(
                user=request.user,
                api_name=ai_engine,
                operation='content_generation',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time=response_time,
                status='success'
            )
            usage.calculate_cost()
            usage.save()
        except Exception as e:
            print(f"Error logging API usage: {str(e)}")

    # Render the bullet points to HTML
    bullet_html = ''
    for idx, bullet_text in enumerate(bullets):
        bullet_html += render_to_string('resumes/partials/bullet_point_form_row.html', {
            'parent_index': parent_index,
            'index': idx,
            'bullet_text': bullet_text,
        })

    # Return the HTML
    return HttpResponse(bullet_html)


@login_required
@require_http_methods(["GET"])
def enhance_bullet(request):
    """
    Enhance a single bullet point using AI.
    This is an HTMX endpoint that returns the enhanced text.
    """
    bullet_text = request.GET.get('bullet_text', '')
    ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Default to ChatGPT
    enhancement_type = request.GET.get('enhancement_type', 'general')
    job_description = request.GET.get('job_description', '')

    # Try to get text from the included textarea if not provided directly
    if not bullet_text:
        for key, value in request.GET.items():
            if key.startswith('bullet_') and value:
                bullet_text = value
                break

    if not bullet_text:
        return HttpResponse("No bullet text found to enhance", status=400)

    # Start timing for API response
    start_time = time.time()

    # Choose AI engine based on user selection
    if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
        enhanced_text, input_tokens, output_tokens = enhance_bullet_chatgpt(
            bullet_text,
            enhancement_type,
            job_description
        )
    elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
        enhanced_text, input_tokens, output_tokens = enhance_bullet_gemini(
            bullet_text,
            enhancement_type,
            job_description
        )
    else:
        # Fallback to basic enhancement
        enhanced_text = enhance_bullet_basic(bullet_text)
        input_tokens = output_tokens = 0

    # Calculate API response time
    response_time = time.time() - start_time

    # Log API usage if using AI
    if (ai_engine == 'chatgpt' and settings.OPENAI_API_KEY) or (
            ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY):
        try:
            # Create API usage record
            usage = APIUsage(
                user=request.user,
                api_name=ai_engine,
                operation='content_enhancement',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time=response_time,
                status='success'
            )
            usage.calculate_cost()
            usage.save()
        except Exception as e:
            print(f"Error logging API usage: {str(e)}")

    # Return the enhanced text
    return HttpResponse(enhanced_text)




@login_required
@require_http_methods(["GET"])
def ats_optimize_bullet(request):
    """
    Optimize a bullet point for ATS systems using AI.
    This is an HTMX endpoint that returns the optimized text.
    """
    bullet_text = request.GET.get('bullet_text', '')
    job_description = request.GET.get('job_description', '')
    ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Default to ChatGPT

    # Try to get bullet text from form
    if not bullet_text:
        for key, value in request.GET.items():
            if key.startswith('bullet_') and value:
                bullet_text = value
                break

    if not bullet_text:
        return HttpResponse("No bullet text provided", status=400)

    # If job description not provided, try to get from active job target
    if not job_description:
        # Look for recent job inputs from this user
        try:
            job_input = JobInput.objects.filter(user=request.user).order_by('-created_at').first()
            if job_input:
                job_description = job_input.job_description
        except:
            pass  # Continue without job description

    # Start timing for API response
    start_time = time.time()

    # Choose AI engine based on user selection
    if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
        optimized_text, input_tokens, output_tokens = ats_optimize_chatgpt(bullet_text, job_description)
    elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
        optimized_text, input_tokens, output_tokens = ats_optimize_gemini(bullet_text, job_description)
    else:
        # If no AI available, return original text
        return HttpResponse(bullet_text)

    # Calculate API response time
    response_time = time.time() - start_time

    # Log API usage
    if (ai_engine == 'chatgpt' and settings.OPENAI_API_KEY) or (
            ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY):
        try:
            # Create API usage record
            usage = APIUsage(
                user=request.user,
                api_name=ai_engine,
                operation='content_generation',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time=response_time,
                status='success'
            )
            usage.calculate_cost()
            usage.save()
        except Exception as e:
            print(f"Error logging API usage: {str(e)}")

    # Return the optimized text
    return HttpResponse(optimized_text)


@login_required
def check_bullet_strength(request):
    """
    Evaluate the strength of a bullet point and provide feedback.
    This is an HTMX endpoint that returns HTML for the feedback.
    """
    bullet_text = request.GET.get('bullet_text', '')

    if not bullet_text:
        return HttpResponse("")

    # Analyze the bullet point
    score = 0
    feedback = []

    # Check for action verbs at beginning
    action_verbs = ["Achieved", "Analyzed", "Built", "Coordinated", "Created", "Delivered",
                    "Designed", "Developed", "Established", "Generated", "Implemented",
                    "Improved", "Led", "Managed", "Optimized", "Reduced", "Spearheaded",
                    "Launched", "Executed", "Streamlined", "Transformed", "Increased",
                    "Directed", "Orchestrated", "Pioneered", "Restructured"]

    starts_with_action = any(bullet_text.startswith(verb) for verb in action_verbs)
    if starts_with_action:
        score += 2
    else:
        feedback.append("Start with a strong action verb")

    # Check for metrics/quantifiable results
    has_numbers = any(c.isdigit() for c in bullet_text)
    if has_numbers:
        score += 2
        # Check for percentage or dollar amounts
        if '%' in bullet_text or '$' in bullet_text:
            score += 1
    else:
        feedback.append("Add measurable results (numbers, %, $)")

    # Check length
    if 80 <= len(bullet_text) <= 150:
        score += 2
    elif len(bullet_text) < 80:
        feedback.append("Too brief - expand with more details")
        score += 0
    else:
        feedback.append("Too lengthy - try to be more concise")
        score += 0

    # Generate rating based on score
    if score >= 5:
        rating = "Excellent! ★★★★★"
        color = "text-success"
    elif score >= 3:
        rating = "Good ★★★★☆"
        color = "text-success"
    elif score >= 2:
        rating = "Average ★★★☆☆"
        color = "text-warning"
    else:
        rating = "Needs improvement ★★☆☆☆"
        color = "text-error"

    # Construct feedback HTML
    result = f'<span class="{color}">{rating}</span>'

    if feedback:
        result += f' <span class="text-xs text-gray-500">Tip: {feedback[0]}</span>'

    return HttpResponse(result)


@login_required
def get_ai_usage_stats(request):
    """
    Get AI usage statistics for the current user.
    Returns a JSON response with usage data.
    """
    # Get time period from request
    period = request.GET.get('period', 'month')  # 'day', 'week', 'month', 'all'

    # Calculate date filter based on period
    if period == 'day':
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = timezone.now() - timezone.timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now() - timezone.timedelta(days=30)
    else:  # 'all'
        start_date = None

    # Query API usage
    query = APIUsage.objects.filter(user=request.user)
    if start_date:
        query = query.filter(timestamp__gte=start_date)

    # Aggregate by API type
    chatgpt_usage = query.filter(api_name='chatgpt')
    gemini_usage = query.filter(api_name='gemini')

    # Calculate totals
    chatgpt_cost = sum([usage.cost for usage in chatgpt_usage])
    gemini_cost = sum([usage.cost for usage in gemini_usage])
    chatgpt_tokens = sum([usage.total_tokens for usage in chatgpt_usage])
    gemini_tokens = sum([usage.total_tokens for usage in gemini_usage])

    # Count operations
    operation_counts = {}
    for op in APIUsage.OPERATION_TYPES:
        op_code = op[0]
        operation_counts[op_code] = query.filter(operation=op_code).count()

    # Prepare response data
    data = {
        'period': period,
        'usage': {
            'chatgpt': {
                'cost': str(chatgpt_cost),
                'tokens': chatgpt_tokens,
                'count': chatgpt_usage.count()
            },
            'gemini': {
                'cost': str(gemini_cost),
                'tokens': gemini_tokens,
                'count': gemini_usage.count()
            }
        },
        'operations': operation_counts,
        'total_cost': str(chatgpt_cost + gemini_cost),
        'total_requests': query.count()
    }

    return JsonResponse(data)


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



@login_required
def resume_creation_choice(request):
    """
    Display a page for users to choose between creating a new resume or uploading an existing one.
    """
    return render(request, 'resumes/resume_creation_choice.html')


@login_required
def upload_resume(request):
    """
    Handle resume upload and AI-based parsing process.
    """
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get uploaded file
                uploaded_file = request.FILES['resume_file']

                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False,
                                                 suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                # Process with ChatGPT
                processed_data = process_resume_with_chatgpt(temp_file_path)

                # Clean up temp file
                os.unlink(temp_file_path)

                if not processed_data:
                    messages.error(request, "Failed to process resume. Please try again or create manually.")
                    return redirect('job_portal:upload_resume')

                # Store processed data in session for next steps
                request.session['resume_form_data'] = processed_data
                request.session['resume_wizard_step'] = 1  # Start at personal info step

                # Track API usage
                APIUsage.objects.create(
                    user=request.user,
                    api_type='chatgpt',
                    endpoint='resume_parse',
                    input_tokens=processed_data.get('input_tokens', 0),
                    output_tokens=processed_data.get('output_tokens', 0)
                )

                messages.success(request, "Resume processed successfully! Review and edit the information.")
                return redirect('job_portal:resume_wizard', step=1)

            except Exception as e:
                messages.error(request, f"Error processing resume: {str(e)}")
                return redirect('job_portal:upload_resume')
    else:
        form = ResumeUploadForm()

    return render(request, 'resumes/upload_resume.html', {'form': form})
