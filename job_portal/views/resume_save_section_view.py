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
                # Updated to include address, linkedin, github, portfolio
                resume.address = personal_info.get('address', resume.address)
                resume.linkedin = personal_info.get('linkedin', resume.linkedin)
                resume.github = personal_info.get('github', resume.github)
                resume.portfolio = personal_info.get('portfolio', resume.portfolio)
                # profile_picture is typically handled by a file upload separate from section data
                resume.save()

            elif section == 'summary':
                summary_data = form_data.get('summary', {})
                resume.summary = summary_data.get('summary', resume.summary)
                resume.save()

            elif section == 'skills':
                # Clear existing skills
                Skill.objects.filter(resume=resume).delete()
                for skill_data in form_data.get('skills', []):
                    skill_name = skill_data.get('Skill name')
                    category_from_parser = skill_data.get('Category')
                    other_category_from_parser = skill_data.get('Other category')
                    proficiency_level = skill_data.get('Estimated proficiency level')

                    if skill_name:
                        skill_category_choice = 'other'  # Default to 'other'
                        skill_category_other_val = None

                        # Map parser categories to model choices based on models.py
                        if category_from_parser:
                            lower_category = category_from_parser.lower()
                            if lower_category in ['technical', 'programming languages', 'frameworks', 'tools']:
                                skill_category_choice = 'technical'
                            elif lower_category == 'soft skills':
                                skill_category_choice = 'soft'
                            elif lower_category == 'language':
                                skill_category_choice = 'language'
                            elif lower_category == 'tool':
                                skill_category_choice = 'tool'
                            elif lower_category == 'other' and other_category_from_parser:
                                skill_category_choice = 'other'
                                skill_category_other_val = other_category_from_parser
                            else:
                                # If category from parser doesn't match predefined, use it as 'other'
                                skill_category_choice = 'other'
                                skill_category_other_val = category_from_parser # Use the parser's category text as other

                        Skill.objects.create(
                            resume=resume,
                            skill_name=skill_name,
                            skill_category_choice=skill_category_choice,
                            skill_category_other=skill_category_other_val,
                            # Ensure proficiency_level is within 0-100 and default to 0 if not valid
                            proficiency_level=int(proficiency_level) if isinstance(proficiency_level, (int, float)) and 0 <= proficiency_level <= 100 else 0
                        )

            elif section == 'experience':
                Experience.objects.filter(resume=resume).delete()
                for exp_data in form_data.get('experiences', []):
                    experience = Experience.objects.create(
                        resume=resume,
                        job_title=exp_data.get('Job title', ''),
                        employer=exp_data.get('Employer/Company name', ''), # Matches parser field
                        location=exp_data.get('Location', ''),
                        start_date=exp_data.get('Start date'),
                        end_date=exp_data.get('End date'),
                        is_current=exp_data.get('Is current job', False)
                    )
                    for bullet in exp_data.get('Bullet points', []):
                        if bullet:
                            ExperienceBulletPoint.objects.create(experience=experience, description=bullet)

            elif section == 'education':
                Education.objects.filter(resume=resume).delete()
                for edu_data in form_data.get('education', []):
                    Education.objects.create(
                        resume=resume,
                        school_name=edu_data.get('School name', ''),
                        location=edu_data.get('Location', ''),
                        degree_name=edu_data.get('Degree', ''), # Maps 'Degree' from parser to 'degree_name'
                        degree_type=edu_data.get('Degree type', ''), # Maps 'Degree type' from parser to 'degree_type'
                        field_of_study=edu_data.get('Field of study', ''),
                        graduation_date=edu_data.get('Graduation date'),
                        gpa=edu_data.get('GPA'),
                        description=edu_data.get('Description', '') # Now includes 'description' field
                    )

            elif section == 'projects':
                Project.objects.filter(resume=resume).delete()
                for proj_data in form_data.get('projects', []):
                    project = Project.objects.create(
                        resume=resume,
                        project_name=proj_data.get('Project name', ''),
                        summary=proj_data.get('Summary/description', ''), # Maps 'Summary/description' to 'summary'
                        start_date=proj_data.get('Start date'),
                        completion_date=proj_data.get('Completion date'),
                        project_link=proj_data.get('Project URL'), # Maps 'Project URL' to 'project_link'
                        github_link=proj_data.get('GitHub URL') # Maps 'GitHub URL' to 'github_link'
                    )
                    for bullet in proj_data.get('Bullet points', []):
                        if bullet:
                            ProjectBulletPoint.objects.create(project=project, description=bullet)

            elif section == 'certifications':
                Certification.objects.filter(resume=resume).delete()
                for cert_data in form_data.get('certifications', []):
                    Certification.objects.create(
                        resume=resume,
                        name=cert_data.get('Name', ''),
                        issuing_organization=cert_data.get('Institute/Issuing organization', ''), # Maps to 'issuing_organization'
                        completion_date=cert_data.get('Completion date'),
                        expiration_date=cert_data.get('Expiration date'),
                        score=cert_data.get('Score', ''),
                        link=cert_data.get('URL/Link', ''), # Maps to 'link'
                        description=cert_data.get('Description', '')
                    )

            elif section == 'languages':
                Language.objects.filter(resume=resume).delete()
                for lang_data in form_data.get('languages', []):
                    # Maps 'Proficiency (0-100 where 100 is native and 0 is basic)' to 'proficiency_level'
                    proficiency = lang_data.get('Proficiency (0-100 where 100 is native and 0 is basic)')
                    # Ensure proficiency is an integer within range 0-100
                    proficiency_level = int(proficiency) if isinstance(proficiency, (int, float)) and 0 <= proficiency <= 100 else 0
                    Language.objects.create(
                        resume=resume,
                        language_name=lang_data.get('Language name', ''),
                        proficiency_level=proficiency_level
                    )

            elif section == 'custom_data':
                CustomData.objects.filter(resume=resume).delete()
                # Assuming form_data now directly reflects the parser's 'Custom Sections' structure
                # where it's a list of sections, each containing entries.
                custom_section_order = 0 # To provide an 'order' for CustomData model
                for custom_section_data in form_data.get('custom_sections', []):
                    section_title = custom_section_data.get('Section title')
                    entries = custom_section_data.get('Entries', [])
                    for entry_data in entries:
                        if entry_data.get('Entry title'): # Only create if there's an entry title
                            CustomData.objects.create(
                                resume=resume,
                                section_name=section_title,
                                entry_title=entry_data.get('Entry title', ''),
                                start_date=entry_data.get('Start date'),
                                end_date=entry_data.get('End date'),
                                description=entry_data.get('Description', ''),
                                link=entry_data.get('Link', ''),
                                order=custom_section_order # Assign an incremental order
                            )
                            custom_section_order += 1 # Increment order for next entry

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
        # Check if redirect args are present, otherwise default to a safe URL
        if resume_id and section:
            return redirect('job_portal:edit_resume_section', resume_id=resume_id, section=section)
        else:
            return redirect('some_default_error_or_dashboard_url') # Replace with an appropriate fallback URL

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.shortcuts import redirect, get_object_or_404
# from django.views.decorators.http import require_http_methods
#
# from job_portal.models import (
#     Resume, Skill, Experience, ExperienceBulletPoint,
#     Education, Certification, Project, ProjectBulletPoint,
#     Language, CustomData
# )
#
#
# @login_required
# @require_http_methods(["POST"])
# def save_section(request, resume_id):
#     """
#     Save a specific section of a resume that has been edited.
#     """
#     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
#     section = request.session.get('edit_section', '')
#     form_data = request.session.get('resume_form_data', {})
#
#     try:
#         with transaction.atomic():
#             # Update the appropriate section
#             if section == 'personal':
#                 personal_info = form_data.get('personal_info', {})
#                 resume.first_name = personal_info.get('first_name', resume.first_name)
#                 resume.mid_name = personal_info.get('mid_name', resume.mid_name)
#                 resume.last_name = personal_info.get('last_name', resume.last_name)
#                 resume.email = personal_info.get('email', resume.email)
#                 resume.phone = personal_info.get('phone', resume.phone)
#                 resume.address = personal_info.get('address', resume.address)
#                 resume.linkedin = personal_info.get('linkedin', resume.linkedin)
#                 resume.github = personal_info.get('github', resume.github)
#                 resume.portfolio = personal_info.get('portfolio', resume.portfolio)
#                 resume.save()
#
#             elif section == 'summary':
#                 summary = form_data.get('summary', '')
#                 if isinstance(summary, dict):
#                     summary = summary.get('summary', '')
#                 resume.summary = summary
#                 resume.save()
#
#             elif section == 'skills':
#                 # Clear existing skills
#                 resume.skills.all().delete()
#
#                 # Add new skills
#                 for skill_data in form_data.get('skills', []):
#                     Skill.objects.create(
#                         resume=resume,
#                         skill_name=skill_data.get('skill_name', ''),
#                         skill_type=skill_data.get('skill_type', 'technical'),
#                         proficiency_level=skill_data.get('proficiency_level', 0)
#                     )
#
#             elif section == 'experience':
#                 # Clear existing experiences
#                 for exp in resume.experiences.all():
#                     exp.bullet_points.all().delete()
#                 resume.experiences.all().delete()
#
#                 # Add new experiences
#                 for exp_data in form_data.get('experiences', []):
#                     experience = Experience.objects.create(
#                         resume=resume,
#                         job_title=exp_data.get('job_title', ''),
#                         employer=exp_data.get('employer', ''),
#                         location=exp_data.get('location', ''),
#                         start_date=exp_data.get('start_date') or None,
#                         end_date=exp_data.get('end_date') if not exp_data.get('is_current', False) else None,
#                         is_current=exp_data.get('is_current', False)
#                     )
#
#                     # Add bullet points
#                     for bullet_data in exp_data.get('bullet_points', []):
#                         bullet_text = bullet_data
#                         # Handle both string and dict formats for bullet points
#                         if isinstance(bullet_data, dict):
#                             bullet_text = bullet_data.get('description', '')
#
#                         if bullet_text:
#                             ExperienceBulletPoint.objects.create(
#                                 experience=experience,
#                                 description=bullet_text
#                             )
#
#             elif section == 'education':
#                 # Clear existing education
#                 resume.educations.all().delete()
#
#                 # Add new education
#                 for edu_data in form_data.get('educations', []):
#                     Education.objects.create(
#                         resume=resume,
#                         school_name=edu_data.get('school_name', ''),
#                         location=edu_data.get('location', ''),
#                         degree=edu_data.get('degree', ''),
#                         degree_type=edu_data.get('degree_type', 'bachelor'),
#                         field_of_study=edu_data.get('field_of_study', ''),
#                         graduation_date=edu_data.get('graduation_date') or None,
#                         gpa=edu_data.get('gpa') or None
#                     )
#
#             elif section == 'projects':
#                 # Clear existing projects
#                 for proj in resume.projects.all():
#                     proj.bullet_points.all().delete()
#                 resume.projects.all().delete()
#
#                 # Add new projects
#                 for proj_data in form_data.get('projects', []):
#                     project = Project.objects.create(
#                         resume=resume,
#                         project_name=proj_data.get('project_name', ''),
#                         summary=proj_data.get('summary', ''),
#                         start_date=proj_data.get('start_date') or None,
#                         completion_date=proj_data.get('completion_date') or None,
#                         project_link=proj_data.get('project_link', ''),
#                         github_link=proj_data.get('github_link', '')
#                     )
#
#                     # Add bullet points
#                     for bullet_text in proj_data.get('bullet_points', []):
#                         if bullet_text:
#                             ProjectBulletPoint.objects.create(
#                                 project=project,
#                                 description=bullet_text
#                             )
#
#             elif section == 'certifications':
#                 # Clear existing certifications
#                 resume.certifications.all().delete()
#
#                 # Add new certifications
#                 for cert_data in form_data.get('certifications', []):
#                     Certification.objects.create(
#                         resume=resume,
#                         name=cert_data.get('name', ''),
#                         institute=cert_data.get('institute', ''),
#                         completion_date=cert_data.get('completion_date') or None,
#                         expiration_date=cert_data.get('expiration_date') or None,
#                         score=cert_data.get('score', ''),
#                         link=cert_data.get('link', ''),
#                         description=cert_data.get('description', '')
#                     )
#
#             elif section == 'languages':
#                 # Clear existing languages
#                 resume.languages.all().delete()
#
#                 # Add new languages
#                 for lang_data in form_data.get('languages', []):
#                     Language.objects.create(
#                         resume=resume,
#                         language_name=lang_data.get('language_name', ''),
#                         proficiency=lang_data.get('proficiency', 'basic')
#                     )
#
#             elif section == 'custom':
#                 # Clear existing custom sections
#                 resume.custom_data.all().delete()
#
#                 # Add new custom sections
#                 for custom_data in form_data.get('custom_sections', []):
#                     if custom_data.get('name'):
#                         CustomData.objects.create(
#                             resume=resume,
#                             name=custom_data.get('name', ''),
#                             completion_date=custom_data.get('completion_date') or None,
#                             bullet_points=custom_data.get('bullet_points', ''),
#                             description=custom_data.get('description', ''),
#                             link=custom_data.get('link', ''),
#                             institution_name=custom_data.get('institution_name', '')
#                         )
#
#         # Clear session data
#         if 'resume_form_data' in request.session:
#             del request.session['resume_form_data']
#         if 'edit_resume_id' in request.session:
#             del request.session['edit_resume_id']
#         if 'edit_section_only' in request.session:
#             del request.session['edit_section_only']
#         if 'edit_section' in request.session:
#             del request.session['edit_section']
#
#         messages.success(request, f"Resume {section} section updated successfully!")
#         return redirect('job_portal:view_resume', resume_id=resume_id)
#
#     except Exception as e:
#         messages.error(request, f"Error updating resume section: {str(e)}")
#         return redirect('job_portal:edit_resume_section', resume_id=resume_id, section=section)