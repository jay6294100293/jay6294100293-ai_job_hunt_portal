# File: job_portal/views/template_selection_view.py
# Path: job_portal/views/template_selection_view.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.http import JsonResponse

from job_portal.models import Resume
from services.supporting_codes.resume_support_code import get_all_template_info, TEMPLATE_CHOICES, \
    get_template_static_info


class TemplateSelectionView(LoginRequiredMixin, View):
    template_html_name = 'resumes/template_select.html'

    def get(self, request, resume_id, *args, **kwargs):
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        templates_information = get_all_template_info()
        next_step_url = reverse('job_portal:edit_resume_section',
                                kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})

        context = {
            'resume': resume,
            'current_template': resume.template_name,
            'templates_info': templates_information,
            'next_step_url': next_step_url,
            'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
        }
        return render(request, self.template_html_name, context)

    def post(self, request, resume_id, *args, **kwargs):
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        selected_template_name = request.POST.get('template_name')

        if not selected_template_name:
            messages.error(request, _("No template was selected. Please choose a template."))
            templates_information = get_all_template_info()
            next_step_url = reverse('job_portal:edit_resume_section',
                                    kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})
            context = {
                'resume': resume,
                'current_template': resume.template_name,
                'templates_info': templates_information,
                'next_step_url': next_step_url,
                'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
            }
            return render(request, self.template_html_name, context)

        # MODIFIED: Validate against TEMPLATE_CHOICES imported from resume_support_code
        valid_templates = [choice[0] for choice in TEMPLATE_CHOICES]

        if selected_template_name in valid_templates:
            resume.template_name = selected_template_name
            resume.save()
            # Determine display name for the message
            display_name = selected_template_name
            for val, name in TEMPLATE_CHOICES:
                if val == selected_template_name:
                    display_name = name
                    break
            messages.success(request,
                             _("Template '{template_display_name}' selected for resume '{resume_title}'. You can now fill in the details.").format(
                                 template_display_name=display_name,
                                 resume_title=resume.title
                             )
                             )
            return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug='personal-info')
        else:
            messages.error(request, _("Invalid template selected ('{selected_template}'). Please try again.").format(
                selected_template=selected_template_name))
            templates_information = get_all_template_info()
            next_step_url = reverse('job_portal:edit_resume_section',
                                    kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})
            context = {
                'resume': resume,
                'current_template': resume.template_name,
                'templates_info': templates_information,
                'next_step_url': next_step_url,
                'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
            }
            return render(request, self.template_html_name, context)


def template_preview_modal(request, template_id):
    """
    AJAX view to return template preview content for modal display
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template_info = get_template_static_info(template_id)
        if template_info:
            preview_url = reverse('job_portal:preview_template', kwargs={'template_id': template_id})
            return JsonResponse({
                'success': True,
                'template_name': template_info['name'],
                'template_description': template_info['description'],
                'preview_url': preview_url
            })
        else:
            return JsonResponse({
                'success': False,
                'error': _('Template not found')
            })

    return JsonResponse({'success': False, 'error': _('Invalid request')})

# # File: job_portal/views/template_selection_view.py
#
# import json


# import re
# import traceback
#
# from decimal import Decimal
#
# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.forms import inlineformset_factory
# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse, Http404
# from django.views.decorators.http import require_http_methods
# from django.db import transaction
#
# from ..models import (
#     Resume, PersonalInfo, Summary, Experience, Education, Skill,
#     Project, Certification, Language, CustomSection,
#     ExperienceBulletPoint, ProjectBulletPoint  # Assuming you have these for detailed bullets
# )
# from ..forms.resume_creation_form import (
#     ResumeBasicInfoForm, ResumeSummaryForm, ExperienceForm,
#     EducationForm, SkillForm, ProjectForm, CertificationForm, LanguageForm, CustomDataForm,
# )
#
#
# try:
#     from services.parser.resume_parser_service import format_date, format_url, format_location, safe_strip
# except ImportError:
#     try:
#         from ..services.parser.resume_parser_service import format_date, format_url, format_location, safe_strip
#     except ImportError:
#         print("Critical Error: Could not import helper functions from services.resume_parser_service.")
#
#
#         def safe_strip(value, default=''):
#             return value.strip() if isinstance(value, str) else default
#
#
#         def format_date(d):
#             return d
#
#
#         def format_url(u):
#             return u
#
#
#         def format_location(l):
#             return l if isinstance(l, str) else ""
#
#
# # --- Helper: Transform Parsed Data ---
# def transform_parsed_data_to_wizard_format(parsed_data):
#     # This function (provided in previous responses) remains the same.
#     # It should return a dictionary structured similarly to DEMO_RESUME_DATA used in preview.
#     print("--- Transforming parsed data to wizard format ---")
#     wizard_data = {}
#     if not isinstance(parsed_data, dict):
#         print(f"Error: parsed_data is not a dictionary (type: {type(parsed_data)}). Returning empty.")
#         return {}
#
#     pi = parsed_data.get('Personal Information', {})
#     if isinstance(pi, dict):
#         raw_email = pi.get('Email')
#         cleaned_email = None
#         if isinstance(raw_email, str):
#             cleaned_email = safe_strip(raw_email.replace('mailto:', ''))
#         wizard_data['personal_info'] = {
#             'first_name': safe_strip(pi.get('First name')), 'mid_name': safe_strip(pi.get('Middle name')),
#             'last_name': safe_strip(pi.get('Last name')), 'email': cleaned_email,
#             'phone': safe_strip(pi.get('Phone number')), 'address': format_location(pi.get('Address')),
#             'linkedin': format_url(pi.get('LinkedIn URL')), 'github': format_url(pi.get('GitHub URL')),
#             'portfolio': format_url(pi.get('Portfolio URL')),
#         }
#     else:
#         wizard_data['personal_info'] = {}
#
#     summary_data = parsed_data.get('Professional Summary')
#     # Ensure key matches model field if Summary is a model (e.g., 'summary_text')
#     wizard_data['summary'] = {'summary_text': safe_strip(summary_data)} if isinstance(summary_data, str) else {
#         'summary_text': ''}
#
#     wizard_data['skills'] = []
#     raw_skills = parsed_data.get('Skills')
#     if isinstance(raw_skills, list):
#         for skill_data in raw_skills:
#             if isinstance(skill_data, dict):
#                 wizard_data['skills'].append({
#                     'skill_name': safe_strip(skill_data.get('Skill name')),
#                     'skill_type': safe_strip(skill_data.get('Skill type'), 'technical'),
#                     'proficiency_level': skill_data.get('Estimated proficiency level', 0),
#                 })
#     elif isinstance(raw_skills, str):  # Handle comma-separated string
#         for skill_name in raw_skills.split(','):
#             if safe_strip(skill_name):
#                 wizard_data['skills'].append(
#                     {'skill_name': safe_strip(skill_name), 'skill_type': 'technical', 'proficiency_level': 0})
#
#     wizard_data['experiences'] = []
#     raw_experience = parsed_data.get('Work Experience')
#     if isinstance(raw_experience, list):
#         for exp_data in raw_experience:
#             if isinstance(exp_data, dict):
#                 main_description = ""
#                 bullet_points_list = []
#                 bullets_raw = exp_data.get('Bullet points', [])
#                 if isinstance(bullets_raw, list):
#                     bullet_points_list = [safe_strip(b) for b in bullets_raw if isinstance(b, str) and safe_strip(b)]
#                 elif isinstance(bullets_raw, str):
#                     bullet_points_list = [safe_strip(b) for b in bullets_raw.split('\n') if safe_strip(b)]
#                 main_description = "\n".join(
#                     [f"• {bp}" for bp in bullet_points_list])  # Or however your Experience model stores this
#
#                 wizard_data['experiences'].append({
#                     'job_title': safe_strip(exp_data.get('Job title')),
#                     'employer': safe_strip(exp_data.get('Employer/Company name')),
#                     'location': format_location(exp_data.get('Location')),
#                     'start_date': format_date(exp_data.get('Start date')),
#                     'end_date': format_date(exp_data.get('End date')),
#                     'is_current': exp_data.get('Is current job', False),
#                     'description': main_description,
#                     'bullet_points_data': bullet_points_list  # For separate ExperienceBulletPoint model
#                 })
#
#     wizard_data['educations'] = []
#     raw_education = parsed_data.get('Education')
#     if isinstance(raw_education, list):
#         for edu_data in raw_education:
#             if isinstance(edu_data, dict):
#                 gpa_val = None
#                 try:
#                     gpa_str = edu_data.get('GPA')
#                     if gpa_str is not None:
#                         cleaned_gpa_str = re.sub(r"[^0-9.]", "", str(gpa_str))
#                         gpa_val = Decimal(cleaned_gpa_str) if cleaned_gpa_str else None
#                 except Exception:
#                     gpa_val = None
#                 wizard_data['educations'].append({
#                     'school_name': safe_strip(edu_data.get('School name')),
#                     'location': format_location(edu_data.get('Location')),
#                     'degree': safe_strip(edu_data.get('Degree')),
#                     'degree_type': safe_strip(edu_data.get('Degree type'),
#                                               Education.DEGREE_TYPES[0][0] if hasattr(Education,
#                                                                                       'DEGREE_TYPES') and Education.DEGREE_TYPES else 'bachelor'),
#                     'field_of_study': safe_strip(edu_data.get('Field of study')),
#                     'graduation_date': format_date(edu_data.get('Graduation date')),
#                     'gpa': gpa_val,
#                     'description': safe_strip(edu_data.get('Description', '')),
#                     # Assuming Education model has a description field
#                 })
#
#     wizard_data['projects'] = []
#     raw_projects = parsed_data.get('Projects')
#     if isinstance(raw_projects, list):
#         for proj_data in raw_projects:
#             if isinstance(proj_data, dict):
#                 summary_desc = safe_strip(proj_data.get('Summary/description'))
#                 bullet_points_list = []
#                 bullets_raw = proj_data.get('Bullet points', [])
#                 if isinstance(bullets_raw, list):
#                     bullet_points_list = [safe_strip(b) for b in bullets_raw if isinstance(b, str) and safe_strip(b)]
#                 elif isinstance(bullets_raw, str):
#                     bullet_points_list = [safe_strip(b) for b in bullets_raw.split('\n') if safe_strip(b)]
#
#                 # Example: combine summary and bullets if Project model description field expects it
#                 full_description = summary_desc
#                 if bullet_points_list:
#                     full_description += "\n" + "\n".join([f"• {bp}" for bp in bullet_points_list])
#
#                 wizard_data['projects'].append({
#                     'project_name': safe_strip(proj_data.get('Project name')),
#                     'summary': summary_desc,  # If Project model has a separate summary field
#                     'description': full_description,  # Or just the combined description
#                     'start_date': format_date(proj_data.get('Start date')),
#                     'completion_date': format_date(proj_data.get('Completion date')),
#                     'project_link': format_url(proj_data.get('Project URL')),
#                     'github_link': format_url(proj_data.get('GitHub URL')),
#                     'technologies_used': safe_strip(proj_data.get('Technologies used')),
#                     'bullet_points_data': bullet_points_list  # For separate ProjectBulletPoint model
#                 })
#
#     wizard_data['certifications'] = []
#     raw_certs = parsed_data.get('Certifications')
#     if isinstance(raw_certs, list):
#         for cert_data in raw_certs:
#             if isinstance(cert_data, dict):
#                 wizard_data['certifications'].append({
#                     'name': safe_strip(cert_data.get('Name')),
#                     'institute': safe_strip(cert_data.get('Institute/Issuing organization')),
#                     'completion_date': format_date(cert_data.get('Completion date')),
#                     'expiration_date': format_date(cert_data.get('Expiration date')),
#                     'score': safe_strip(cert_data.get('Score')),
#                     'link': format_url(cert_data.get('URL/Link')),
#                     'description': safe_strip(cert_data.get('Description')),
#                 })
#
#     wizard_data['languages'] = []
#     raw_langs = parsed_data.get('Languages')
#     if isinstance(raw_langs, list):
#         for lang_data in raw_langs:
#             if isinstance(lang_data, dict):
#                 wizard_data['languages'].append({
#                     'language_name': safe_strip(lang_data.get('Language name')),
#                     'proficiency': safe_strip(lang_data.get('Proficiency'),
#                                               Language.PROFICIENCY_LEVELS[0][0] if hasattr(Language,
#                                                                                            'PROFICIENCY_LEVELS') and Language.PROFICIENCY_LEVELS else 'basic'),
#                 })
#
#     wizard_data['custom_sections'] = []
#     raw_custom = parsed_data.get('Additional sections')  # Key from parser
#     if isinstance(raw_custom, list):
#         for custom_data_item in raw_custom:  # Renamed loop variable
#             if isinstance(custom_data_item, dict):
#                 bullets_raw = custom_data_item.get('Bullet points', [])
#                 formatted_bullets_str = ""
#                 if isinstance(bullets_raw, list):
#                     formatted_bullets_str = "\n".join(
#                         f"• {safe_strip(b)}" for b in bullets_raw if isinstance(b, str) and safe_strip(b))
#                 elif isinstance(bullets_raw, str):
#                     lines = [safe_strip(b) for b in bullets_raw.split('\n') if safe_strip(b)]
#                     formatted_bullets_str = "\n".join(
#                         f"• {line}" if not line.startswith(('•', '*', '-')) else line for line in lines)
#
#                 wizard_data['custom_sections'].append({
#                     'title': safe_strip(custom_data_item.get('Section name')),
#                     # Ensure this maps to your CustomSection model's 'title' field
#                     'institution_name': safe_strip(custom_data_item.get('Institution name')),
#                     'location': safe_strip(custom_data_item.get('Location')),
#                     'completion_date': format_date(custom_data_item.get('Completion date')),
#                     'link': format_url(custom_data_item.get('URL/Link')),
#                     'description': safe_strip(custom_data_item.get('Description')),
#                     'bullet_points': formatted_bullets_str,  # This should map to a field in your CustomSection model
#                 })
#     print("--- Transformation complete ---")
#     return wizard_data
#
#
# # --- Helper: Populate DB from Transformed Data ---
# @transaction.atomic
# def populate_resume_from_transformed_data(resume_instance, transformed_data):
#     print(f"Populating resume ID {resume_instance.id} from transformed data.")
#     # Personal Info
#     if 'personal_info' in transformed_data and transformed_data['personal_info']:
#         PersonalInfo.objects.update_or_create(resume=resume_instance, defaults=transformed_data['personal_info'])
#         print("  Updated/Created PersonalInfo.")
#     # Summary
#     if 'summary' in transformed_data and transformed_data['summary'].get('summary_text'):
#         Summary.objects.update_or_create(resume=resume_instance,
#                                          defaults={'summary_text': transformed_data['summary']['summary_text']})
#         print("  Updated/Created Summary.")
#     # Experiences
#     if 'experiences' in transformed_data:
#         resume_instance.experiences_data.all().delete()  # Use related_name
#         for exp_data_item in transformed_data['experiences']:  # Renamed loop variable
#             bullets_list = exp_data_item.pop('bullet_points_data', [])
#             exp = Experience.objects.create(resume=resume_instance, **exp_data_item)
#             for bp_text in bullets_list: ExperienceBulletPoint.objects.create(experience=exp, description=bp_text)
#         print(f"  Added {len(transformed_data['experiences'])} experiences.")
#     # Education
#     if 'educations' in transformed_data:
#         resume_instance.educations_data.all().delete()  # Use related_name
#         for edu_data_item in transformed_data['educations']: Education.objects.create(resume=resume_instance,
#                                                                                       **edu_data_item)  # Renamed loop variable
#         print(f"  Added {len(transformed_data['educations'])} education entries.")
#     # Skills
#     if 'skills' in transformed_data:
#         resume_instance.skills_data.all().delete()  # Use related_name
#         for skill_data_item in transformed_data['skills']: Skill.objects.create(resume=resume_instance,
#                                                                                 **skill_data_item)  # Renamed loop variable
#         print(f"  Added {len(transformed_data['skills'])} skills.")
#     # Projects
#     if 'projects' in transformed_data:
#         resume_instance.projects_data.all().delete()  # Use related_name
#         for proj_data_item in transformed_data['projects']:  # Renamed loop variable
#             bullets_list = proj_data_item.pop('bullet_points_data', [])
#             proj = Project.objects.create(resume=resume_instance, **proj_data_item)
#             for bp_text in bullets_list: ProjectBulletPoint.objects.create(project=proj, description=bp_text)
#         print(f"  Added {len(transformed_data['projects'])} projects.")
#     # Certifications
#     if 'certifications' in transformed_data:
#         resume_instance.certifications_data.all().delete()  # Use related_name
#         for cert_data_item in transformed_data['certifications']: Certification.objects.create(resume=resume_instance,
#                                                                                                **cert_data_item)  # Renamed loop variable
#         print(f"  Added {len(transformed_data['certifications'])} certifications.")
#     # Languages
#     if 'languages' in transformed_data:
#         resume_instance.languages_data.all().delete()  # Use related_name
#         for lang_data_item in transformed_data['languages']: Language.objects.create(resume=resume_instance,
#                                                                                      **lang_data_item)  # Renamed loop variable
#         print(f"  Added {len(transformed_data['languages'])} languages.")
#     # Custom Sections
#     if 'custom_sections' in transformed_data:
#         resume_instance.custom_sections_data.all().delete()  # Use related_name
#         for custom_item_data in transformed_data['custom_sections']: CustomSection.objects.create(
#             resume=resume_instance, **custom_item_data)
#         print(f"  Added {len(transformed_data['custom_sections'])} custom sections.")
#
#
# # --- Main Views ---
# @login_required
# def template_selection(request):
#     print("==== DB-BASED: ENTERING template_selection VIEW ====")
#     draft_resume_id = request.session.get('draft_resume_id')
#     if not draft_resume_id:
#         messages.error(request, "No draft resume found. Please start by creating a new resume.")
#         return redirect('job_portal:resume_create_choice')
#     try:
#         resume = Resume.objects.get(id=draft_resume_id, user=request.user)
#     except Resume.DoesNotExist:
#         messages.error(request, "Draft resume not found or access denied.")
#         request.session.pop('draft_resume_id', None)
#         return redirect('job_portal:resume_create_choice')
#
#     from_upload = request.session.get('from_resume_upload', False)
#     # This template list should ideally come from a service or model
#     # For now, using the hardcoded one from your template_select.html's context
#     templates_data = [
#         {'id': 1, 'name': 'Professional Classic', 'description': 'A clean and traditional format, ATS-friendly.',
#          'thumbnail': 'img/templates/1.jpg', 'tags': ['Classic', 'ATS-Friendly', 'Traditional']},
#         {'id': 2, 'name': 'Modern Minimalist', 'description': 'Sleek design focusing on readability and key info.',
#          'thumbnail': 'img/templates/2.jpg', 'tags': ['Modern', 'Minimalist', 'Clean']},
#         {'id': 3, 'name': 'Executive Style', 'description': 'Elegant and formal, suitable for senior roles.',
#          'thumbnail': 'img/templates/3.jpg', 'tags': ['Executive', 'Formal', 'Senior Level']},
#         {'id': 4, 'name': 'Technical Focus',
#          'description': 'Highlights technical skills, projects, and certifications.',
#          'thumbnail': 'img/templates/4.jpg', 'tags': ['Technical', 'Skills-Focused', 'IT']},
#         {'id': 5, 'name': 'Clean Professional',
#          'description': 'A modern take on professional resumes with clear sections.',
#          'thumbnail': 'img/templates/5.jpg', 'tags': ['Professional', 'Clean', 'Modern']},
#         {'id': 6, 'name': 'Fresh Graduate', 'description': 'Emphasizes education, projects, and internships.',
#          'thumbnail': 'img/templates/6.jpg', 'tags': ['Entry-Level', 'Academic', 'Internship']},
#     ]
#     is_debug = getattr(settings, 'DEBUG', False)
#     context = {
#         'templates': templates_data, 'from_upload': from_upload, 'debug': is_debug,
#         'resume': resume, 'page_title': f"Choose Template for '{resume.title}'",
#     }
#     return render(request, 'resumes/template_select.html', context)
#
#
# @login_required
# @require_http_methods(["POST"])
# @transaction.atomic
# def select_template(request):
#     print("==== DB-BASED: ENTERING select_template VIEW ====")
#     draft_resume_id = request.session.get('draft_resume_id')
#     if not draft_resume_id:
#         messages.error(request, "No draft resume session. Please start over.")
#         return redirect('job_portal:resume_create_choice')
#     try:
#         resume = Resume.objects.get(id=draft_resume_id, user=request.user)
#     except Resume.DoesNotExist:
#         messages.error(request, "Draft resume not found. Please start over.")
#         request.session.pop('draft_resume_id', None)
#         return redirect('job_portal:resume_create_choice')
#
#     template_id_str = request.POST.get('template_id')
#     if not template_id_str:
#         messages.error(request, "Please select a template.")
#         # Need to pass context again if re-rendering template_selection
#         # For simplicity, redirecting, but ideally, re-render with error.
#         return redirect('job_portal:template_selection')
#
#     template_map_for_names = {  # Ensure this map is comprehensive
#         1: 'Professional Classic', 2: 'Modern Minimalist', 3: 'Executive Style',
#         4: 'Technical Focus', 5: 'Clean Professional', 6: 'Fresh Graduate',
#     }
#     try:
#         template_id = int(template_id_str)
#         resume.template_name = template_map_for_names.get(template_id, f"template_{template_id}")  # Fallback name
#         resume.save()
#         print(f"Saved template '{resume.template_name}' for resume ID {resume.id}")
#     except ValueError:
#         messages.error(request, "Invalid template ID.")
#         return redirect('job_portal:template_selection')
#
#     if request.session.get('from_resume_upload', False):
#         print(f"Processing uploaded resume data for DB population (Resume ID: {resume.id})...")
#         parsed_data_json = request.session.get('parsed_resume_data')
#         if parsed_data_json:
#             try:
#                 parsed_data = json.loads(parsed_data_json)
#                 transformed_data = transform_parsed_data_to_wizard_format(parsed_data)
#                 populate_resume_from_transformed_data(resume, transformed_data)
#                 if 'parsed_resume_data' in request.session: del request.session['parsed_resume_data']
#                 if 'from_resume_upload' in request.session: del request.session['from_resume_upload']
#                 if 'resume_ai_engine' in request.session: del request.session['resume_ai_engine']
#                 messages.info(request, "Uploaded resume data has been imported. Please review each section.")
#             except Exception as e:  # Catch broader errors during population
#                 print(f"ERROR populating DB from parsed data: {e}");
#                 traceback.print_exc()
#                 messages.error(request,
#                                f"Error processing parsed resume data: {e}. Some data might not have been imported. Please review carefully.")
#         else:
#             messages.warning(request, "Parsed resume data not found in session, but was expected for upload flow.")
#
#     request.session['resume_wizard_step'] = 1
#     request.session.modified = True
#     return redirect('job_portal:resume_wizard', step=1)
#
#
# @login_required
# @require_http_methods(["GET"])
# def preview_template_html(request, template_id):
#     """ Serves the HTML content for a specific resume template preview. """
#     DEMO_RESUME_DATA = {
#         "personal_info": {"full_name": "Jamie P. Developer", "email": "jamie.dev@example.io", "phone": "(555) 123-9876",
#                           "linkedin": "linkedin.com/in/jamiedev", "github": "github.com/jamiedev",
#                           "address": "456 Tech Park, Silicon Valley, CA", "portfolio": "jamiedev.io"},
#         "summary": {
#             "summary_text": "Innovative and detail-oriented Full Stack Developer with a passion for creating efficient, scalable, and user-friendly web applications. Adept at problem-solving and collaborating with cross-functional teams to deliver high-quality software solutions."},
#         "experiences": [{"job_title": "Lead Developer", "employer": "Future Systems Ltd.", "start_date": "Mar 2021",
#                          "end_date": "Present", "location": "Remote", "is_current": True, "bullet_points": [{
#                                                                                                                 "description": "Architected and led the development of a new SaaS platform, increasing user engagement by 30%."},
#                                                                                                             {
#                                                                                                                 "description": "Mentored a team of 8 junior and mid-level developers."}]}],
#         "educations": [{"school_name": "Institute of Technology", "degree": "B.Sc. in Web Development",
#                         "field_of_study": "Computer Engineering", "graduation_date": "Jun 2020",
#                         "location": "Tech City, TC", "gpa": "3.95/4.0"}],
#         "skills": [{"skill_name": "Python/Django", "skill_type": "Backend", "proficiency_level": "Expert"},
#                    {"skill_name": "JavaScript/React", "skill_type": "Frontend", "proficiency_level": "Advanced"},
#                    {"skill_name": "Docker & Kubernetes", "skill_type": "DevOps", "proficiency_level": "Intermediate"}],
#         "projects": [{"project_name": "AI-Powered Job Board Aggregator",
#                       "summary": "Developed a web application that aggregates job listings from various sources and uses NLP to match them with user profiles.",
#                       "bullet_points": [{"description": "Utilized Python, Flask, spaCy, and PostgreSQL."},
#                                         {"description": "Deployed on AWS EC2 with Docker."}]}],
#         "certifications": [{"name": "DjangoCon Certified Professional", "institute": "Django Software Foundation",
#                             "completion_date": "2022"}],
#         "languages": [{"language_name": "English", "proficiency": "Native"},
#                       {"language_name": "German", "proficiency": "Basic"}],
#         "custom_sections": [{"name": "Publications",
#                              "bullet_points": "• 'Advanced Django Techniques', Tech Journal (2023)\n• 'The Future of WebAssembly', Code Monthly (2022)"}]
#     }
#     template_file_map = {  # Ensure this map is accurate
#         1: 'resumes/templates/template1.html', 2: 'resumes/templates/template2.html',
#         3: 'resumes/templates/template3.html', 4: 'resumes/templates/template4.html',
#         5: 'resumes/templates/template5.html', 6: 'resumes/templates/template6.html',
#     }
#     template_to_render = template_file_map.get(template_id)
#     if not template_to_render:
#         return HttpResponse("Template preview not available for this ID.", status=404)
#     context = {
#         'resume_data': DEMO_RESUME_DATA,
#         'template_settings': {'font_family': 'Arial, sans-serif', 'base_font_size': '10pt', 'primary_color': '#2d3748',
#                               'secondary_color': '#2b6cb0', 'accent_color': '#2c5282', 'line_height': '1.4',
#                               'section_spacing': '0.8rem', 'bullet_indent': '1.2rem', },
#         'is_preview': True,
#     }
#     return render(request, template_to_render, context)
#
#
# @login_required
# @transaction.atomic
# def resume_wizard(request, step):
#     print(f"\n==== DB-BASED: resume_wizard VIEW for step {step} ({request.method}) ====")
#     draft_resume_id = request.session.get('draft_resume_id')
#     if not draft_resume_id:
#         messages.error(request, "No active resume draft. Please start again.")
#         return redirect('job_portal:resume_create_choice')
#
#     try:
#         resume_instance = Resume.objects.get(id=draft_resume_id, user=request.user)
#     except Resume.DoesNotExist:
#         messages.error(request, "Resume draft not found. Please start again.")
#         request.session.pop('draft_resume_id', None)
#         return redirect('job_portal:resume_create_choice')
#
#     # Ensure related one-to-one instances exist
#     personal_info_instance, _ = PersonalInfo.objects.get_or_create(resume=resume_instance)
#     summary_instance, _ = Summary.objects.get_or_create(resume=resume_instance)
#
#     # Define Formset factories - ensure related_names match your models
#     ExperienceFormSet = inlineformset_factory(Resume, Experience, form=ExperienceForm, related_name='experiences_data',
#                                               extra=1, can_delete=True, can_order=False)
#     EducationFormSet = inlineformset_factory(Resume, Education, form=EducationForm, related_name='educations_data',
#                                              extra=1, can_delete=True, can_order=False)
#     SkillFormSet = inlineformset_factory(Resume, Skill, form=SkillForm, related_name='skills_data', extra=1,
#                                          can_delete=True, can_order=False)
#     ProjectFormSet = inlineformset_factory(Resume, Project, form=ProjectForm, related_name='projects_data', extra=1,
#                                            can_delete=True, can_order=False)
#     CertificationFormSet = inlineformset_factory(Resume, Certification, form=CertificationForm,
#                                                  related_name='certifications_data', extra=1, can_delete=True,
#                                                  can_order=False)
#     LanguageFormSet = inlineformset_factory(Resume, Language, form=LanguageForm, related_name='languages_data', extra=1,
#                                             can_delete=True, can_order=False)
#     CustomDataFormSet = inlineformset_factory(Resume, CustomSection, form=CustomDataForm,
#                                               related_name='custom_sections_data', extra=1, can_delete=True,
#                                               can_order=False)
#
#     steps_config = {
#         1: {'title': 'Personal Information', 'form_class': ResumeBasicInfoForm, 'instance_obj': personal_info_instance,
#             'template': 'resumes/wizard_steps/personal_info.html'},
#         2: {'title': 'Professional Summary', 'form_class': ResumeSummaryForm, 'instance_obj': summary_instance,
#             'template': 'resumes/wizard_steps/summary.html'},
#         3: {'title': 'Skills', 'formset_class': SkillFormSet, 'template': 'resumes/wizard_steps/skills.html'},
#         4: {'title': 'Work Experience', 'formset_class': ExperienceFormSet,
#             'template': 'resumes/wizard_steps/experience.html'},
#         5: {'title': 'Education', 'formset_class': EducationFormSet, 'template': 'resumes/wizard_steps/education.html'},
#         6: {'title': 'Projects', 'formset_class': ProjectFormSet, 'template': 'resumes/wizard_steps/projects.html'},
#         7: {'title': 'Certifications', 'formset_class': CertificationFormSet,
#             'template': 'resumes/wizard_steps/certifications.html'},
#         8: {'title': 'Languages', 'formset_class': LanguageFormSet, 'template': 'resumes/wizard_steps/languages.html'},
#         9: {'title': 'Additional Sections', 'formset_class': CustomDataFormSet,
#             'template': 'resumes/wizard_steps/custom_sections.html'},
#     }
#
#     try:
#         step = int(step)
#     except ValueError:
#         step = 1
#     if not (1 <= step <= len(steps_config)): step = 1
#     request.session['resume_wizard_step'] = step
#     step_info = steps_config[step]
#     form_or_formset = None  # Initialize
#
#     if request.method == 'POST':
#         is_valid_overall = True
#         if step_info.get('form_class'):
#             form_or_formset = step_info['form_class'](request.POST, instance=step_info['instance_obj'])
#             if form_or_formset.is_valid():
#                 saved_obj = form_or_formset.save(commit=False)
#                 if not hasattr(saved_obj, 'resume_id') or not saved_obj.resume_id:  # Check if resume FK needs setting
#                     if hasattr(saved_obj, 'resume'): saved_obj.resume = resume_instance
#                 saved_obj.save()
#                 print(f"Step {step} form saved for Resume ID {resume_instance.id}.")
#             else:
#                 is_valid_overall = False;
#                 messages.error(request, f"Errors in '{step_info['title']}'.")
#                 print(f"Form errors step {step}: {form_or_formset.errors.as_json()}")
#         elif step_info.get('formset_class'):
#             prefix = f"step{step}_{step_info['title'].lower().replace(' ', '_').replace('/', '_')}"
#             form_or_formset = step_info['formset_class'](request.POST, instance=resume_instance, prefix=prefix)
#             if form_or_formset.is_valid():
#                 form_or_formset.save()
#                 print(f"Step {step} formset saved for Resume ID {resume_instance.id}.")
#             else:
#                 is_valid_overall = False;
#                 messages.error(request, f"Errors in '{step_info['title']}'.")
#                 print(f"Formset errors step {step}: {form_or_formset.errors}")
#
#         if is_valid_overall:
#             request.session.modified = True
#             next_step_val = step + 1
#             if 'save_and_exit' in request.POST:
#                 messages.success(request, f"'{resume_instance.title}' draft saved.")
#                 return redirect('job_portal:my_resumes')
#             elif next_step_val > len(steps_config):
#                 resume_instance.status = 'completed'  # Or a 'review' status
#                 resume_instance.save()
#                 messages.success(request, f"All sections for '{resume_instance.title}' completed.")
#                 # Clear draft_resume_id from session as it's no longer a draft being actively edited by wizard
#                 # request.session.pop('draft_resume_id', None)
#                 # Instead of generate_resume, maybe a review page or dashboard for this resume
#                 return redirect('job_portal:view_resume_detail', resume_id=resume_instance.id)  # Example redirect
#             else:
#                 return redirect('job_portal:resume_wizard', step=next_step_val)
#
#     # GET or re-render after invalid POST
#     if not form_or_formset:
#         if step_info.get('form_class'):
#             form_or_formset = step_info['form_class'](instance=step_info['instance_obj'])
#         elif step_info.get('formset_class'):
#             prefix = f"step{step}_{step_info['title'].lower().replace(' ', '_').replace('/', '_')}"
#             form_or_formset = step_info['formset_class'](instance=resume_instance, prefix=prefix)
#
#     context = {
#         'step': step, 'total_steps': len(steps_config), 'step_title': step_info['title'],
#         'resume': resume_instance, 'previous_step': step - 1 if step > 1 else None,
#         'next_step': step + 1 if step < len(steps_config) else None,
#         'is_final_step': step == len(steps_config),
#         'form' if step_info.get('form_class') else 'formset': form_or_formset,
#     }
#     if step == 3: context['skill_types'] = Skill.SKILL_TYPES
#     if step == 5: context['degree_types'] = Education.DEGREE_TYPES
#     if step == 8: context['proficiency_levels'] = Language.PROFICIENCY_LEVELS
#
#     return render(request, step_info['template'], context)
#
# # # File: job_portal/views/template_selection_view.py
# # # Path: job_portal/views/template_selection_view.py
# #
# # from django.contrib import messages
# # from django.contrib.auth.mixins import LoginRequiredMixin
# # from django.shortcuts import render, redirect, get_object_or_404
# # from django.urls import reverse
# # from django.utils.translation import gettext_lazy as _
# # from django.views import View
# #
# # from job_portal.models import Resume
# # from services.supporting_codes.resume_support_code import get_all_template_info, TEMPLATE_CHOICES
# #
# #
# # # MODIFIED: Import TEMPLATE_CHOICES from resume_support_code as well
# #
# #
# #
# # class TemplateSelectionView(LoginRequiredMixin, View):
# #     template_html_name = 'resumes/template_select.html'
# #
# #     def get(self, request, resume_id, *args, **kwargs):
# #         resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# #         templates_information = get_all_template_info()
# #         next_step_url = reverse('job_portal:edit_resume_section',
# #                                 kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})
# #
# #         context = {
# #             'resume': resume,
# #             'current_template': resume.template_name,
# #             'templates_info': templates_information,
# #             'next_step_url': next_step_url,
# #             'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
# #         }
# #         return render(request, self.template_html_name, context)
# #
# #     def post(self, request, resume_id, *args, **kwargs):
# #         resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# #         selected_template_name = request.POST.get('template_name')
# #
# #         if not selected_template_name:
# #             messages.error(request, _("No template was selected. Please choose a template."))
# #             templates_information = get_all_template_info()
# #             next_step_url = reverse('job_portal:edit_resume_section',
# #                                     kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})
# #             context = {
# #                 'resume': resume,
# #                 'current_template': resume.template_name,
# #                 'templates_info': templates_information,
# #                 'next_step_url': next_step_url,
# #                 'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
# #             }
# #             return render(request, self.template_html_name, context)
# #
# #         # MODIFIED: Validate against TEMPLATE_CHOICES imported from resume_support_code
# #         valid_templates = [choice[0] for choice in TEMPLATE_CHOICES]
# #
# #         if selected_template_name in valid_templates:
# #             resume.template_name = selected_template_name
# #             resume.save()
# #             # Determine display name for the message
# #             display_name = selected_template_name
# #             for val, name in TEMPLATE_CHOICES:
# #                 if val == selected_template_name:
# #                     display_name = name
# #                     break
# #             messages.success(request,
# #                              _("Template '{template_display_name}' selected for resume '{resume_title}'. You can now fill in the details.").format(
# #                                  template_display_name=display_name,
# #                                  resume_title=resume.title
# #                              )
# #                              )
# #             return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug='personal-info')
# #         else:
# #             messages.error(request, _("Invalid template selected ('{selected_template}'). Please try again.").format(
# #                 selected_template=selected_template_name))
# #             templates_information = get_all_template_info()
# #             next_step_url = reverse('job_portal:edit_resume_section',
# #                                     kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})
# #             context = {
# #                 'resume': resume,
# #                 'current_template': resume.template_name,
# #                 'templates_info': templates_information,
# #                 'next_step_url': next_step_url,
# #                 'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
# #             }
# #             return render(request, self.template_html_name, context)