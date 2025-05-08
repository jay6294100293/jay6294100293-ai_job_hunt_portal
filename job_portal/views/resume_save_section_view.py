from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from job_portal.models import (
    Resume, Skill, Experience, ExperienceBulletPoint,
    Education, Certification, Project, ProjectBulletPoint,
    Language, CustomData
)


@login_required
@require_http_methods(["POST"])
def save_section(request, resume_id):
    """
    Save a specific section of a resume that has been edited.
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    section = request.session.get('edit_section', '')
    form_data = request.session.get('resume_form_data', {})

    try:
        with transaction.atomic():
            # Update the appropriate section
            if section == 'personal':
                personal_info = form_data.get('personal_info', {})
                resume.first_name = personal_info.get('first_name', resume.first_name)
                resume.mid_name = personal_info.get('mid_name', resume.mid_name)
                resume.last_name = personal_info.get('last_name', resume.last_name)
                resume.email = personal_info.get('email', resume.email)
                resume.phone = personal_info.get('phone', resume.phone)
                resume.address = personal_info.get('address', resume.address)
                resume.linkedin = personal_info.get('linkedin', resume.linkedin)
                resume.github = personal_info.get('github', resume.github)
                resume.portfolio = personal_info.get('portfolio', resume.portfolio)
                resume.save()

            elif section == 'summary':
                summary = form_data.get('summary', '')
                if isinstance(summary, dict):
                    summary = summary.get('summary', '')
                resume.summary = summary
                resume.save()

            elif section == 'skills':
                # Clear existing skills
                resume.skills.all().delete()

                # Add new skills
                for skill_data in form_data.get('skills', []):
                    Skill.objects.create(
                        resume=resume,
                        skill_name=skill_data.get('skill_name', ''),
                        skill_type=skill_data.get('skill_type', 'technical'),
                        proficiency_level=skill_data.get('proficiency_level', 0)
                    )

            elif section == 'experience':
                # Clear existing experiences
                for exp in resume.experiences.all():
                    exp.bullet_points.all().delete()
                resume.experiences.all().delete()

                # Add new experiences
                for exp_data in form_data.get('experiences', []):
                    experience = Experience.objects.create(
                        resume=resume,
                        job_title=exp_data.get('job_title', ''),
                        employer=exp_data.get('employer', ''),
                        location=exp_data.get('location', ''),
                        start_date=exp_data.get('start_date') or None,
                        end_date=exp_data.get('end_date') if not exp_data.get('is_current', False) else None,
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

            elif section == 'education':
                # Clear existing education
                resume.educations.all().delete()

                # Add new education
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

            elif section == 'projects':
                # Clear existing projects
                for proj in resume.projects.all():
                    proj.bullet_points.all().delete()
                resume.projects.all().delete()

                # Add new projects
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

            elif section == 'certifications':
                # Clear existing certifications
                resume.certifications.all().delete()

                # Add new certifications
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

            elif section == 'languages':
                # Clear existing languages
                resume.languages.all().delete()

                # Add new languages
                for lang_data in form_data.get('languages', []):
                    Language.objects.create(
                        resume=resume,
                        language_name=lang_data.get('language_name', ''),
                        proficiency=lang_data.get('proficiency', 'basic')
                    )

            elif section == 'custom':
                # Clear existing custom sections
                resume.custom_data.all().delete()

                # Add new custom sections
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
        if 'resume_form_data' in request.session:
            del request.session['resume_form_data']
        if 'edit_resume_id' in request.session:
            del request.session['edit_resume_id']
        if 'edit_section_only' in request.session:
            del request.session['edit_section_only']
        if 'edit_section' in request.session:
            del request.session['edit_section']

        messages.success(request, f"Resume {section} section updated successfully!")
        return redirect('job_portal:view_resume', resume_id=resume_id)

    except Exception as e:
        messages.error(request, f"Error updating resume section: {str(e)}")
        return redirect('job_portal:edit_resume_section', resume_id=resume_id, section=section)