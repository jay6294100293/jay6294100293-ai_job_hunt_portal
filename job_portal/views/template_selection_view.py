# job_portal/views/template_selection_view.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from job_portal.models import Resume


@login_required
def template_selection(request, resume_id=None):
    """Displays template options for the user to select."""
    # If resume_id is provided, we're selecting a template for an existing resume
    if resume_id:
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        # Only allow template selection for drafts
        if resume.publication_status != Resume.DRAFT:
            messages.warning(request, "You can only change the template of draft resumes.")
            return redirect('job_portal:view_resume', resume_id=resume_id)
    else:
        resume = None

    # Example templates - replace with your actual template data
    templates = [
        {
            'id': 1, 'name': 'Professional Classic',
            'description': 'A clean and traditional format, ATS-friendly.',
            'thumbnail': 'img/templates/1.jpg',
            'tags': ['Classic', 'ATS-Friendly', 'Traditional']
        },
        {
            'id': 2, 'name': 'Modern Minimalist',
            'description': 'Sleek design focusing on readability and key info.',
            'thumbnail': 'img/templates/2.jpg',
            'tags': ['Modern', 'Minimalist', 'Clean']
        },
        {
            'id': 3, 'name': 'Executive Style',
            'description': 'Elegant and formal, suitable for senior roles.',
            'thumbnail': 'img/templates/3.jpg',
            'tags': ['Executive', 'Formal', 'Senior Level']
        },
        {
            'id': 4, 'name': 'Technical Focus',
            'description': 'Highlights technical skills, projects, and certifications.',
            'thumbnail': 'img/templates/4.jpg',
            'tags': ['Technical', 'Skills-Focused', 'IT']
        },
        {
            'id': 5, 'name': 'Clean Professional',
            'description': 'A modern take on professional resumes with clear sections.',
            'thumbnail': 'img/templates/5.jpg',
            'tags': ['Professional', 'Clean', 'Modern']
        },
        {
            'id': 6, 'name': 'Fresh Graduate',
            'description': 'Emphasizes education, projects, and internships.',
            'thumbnail': 'img/templates/6.jpg',
            'tags': ['Entry-Level', 'Academic', 'Internship']
        },
    ]

    return render(request, 'resumes/template_select.html', {
        'templates': templates,
        'resume': resume,
    })


@login_required
@require_http_methods(["POST"])
def select_template(request, resume_id=None):
    """Handles template selection and updates the resume."""
    template_id = request.POST.get('template_id')
    if not template_id:
        messages.error(request, "Please select a template")
        return redirect('job_portal:template_selection')

    # If resume_id is provided, update existing resume
    if resume_id:
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        resume.template_name = template_id
        resume.save()

        messages.success(request, f"Template updated successfully for '{resume.title}'")
        return redirect('job_portal:view_resume', resume_id=resume.id)
    else:
        # No existing resume, redirect to create new resume
        messages.info(request, "Please create a new resume to use this template")
        return redirect('job_portal:create_resume_meta')


# # job_portal/views/template_selection_view.py
#
# import json
# import re
# import traceback
# from datetime import date
# from decimal import Decimal # <-- Import Decimal
#
# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# # Import BaseFormSet, BaseModelFormSet - Not strictly needed here, but good practice
# from django.forms import formset_factory
# from django.shortcuts import render, redirect
# from django.views.decorators.http import require_http_methods
#
# # Import necessary forms and models
# from ..forms.resume_creation_form import (
#     ResumeBasicInfoForm, ResumeSummaryForm, ExperienceForm,
#     EducationForm, SkillForm, ProjectForm, CertificationForm, LanguageForm, CustomDataForm,
# )
# from ..models import (
#     Skill, Education, Language
# )
#
# # Import helper functions from resume_parser_service
# try:
#     from services.parser.resume_parser_service import format_date, format_url, format_location, safe_strip
# except ImportError:
#     print("Warning: Could not import helper functions from services.resume_parser_service.")
#     # Define fallback functions if import fails
#     def safe_strip(value, default=''): return value.strip() if isinstance(value, str) else default
#     def format_date(d):
#         # Add basic date handling if needed, otherwise just return
#         return d
#     def format_url(u):
#         # Add basic URL handling if needed, otherwise just return
#         return u
#     def format_location(l):
#         # Add basic location handling if needed, otherwise just return
#         return l if isinstance(l, str) else ""
#
#
# # --- transform_parsed_data_to_wizard_format ---
# def transform_parsed_data_to_wizard_format(parsed_data):
#     """Transforms parsed resume data (dict) into the format expected by the wizard's session data."""
#     print("--- Transforming parsed data to wizard format ---")
#     wizard_data = {}
#     if not isinstance(parsed_data, dict):
#         print(f"Error: parsed_data is not a dictionary (type: {type(parsed_data)}). Returning empty.")
#         return {}
#
#     # 1. Personal Information
#     pi = parsed_data.get('Personal Information', {})
#     if isinstance(pi, dict):
#         raw_email = pi.get('Email')
#         cleaned_email = None
#         if isinstance(raw_email, str):
#             # Remove mailto: prefix and strip whitespace
#             cleaned_email = safe_strip(raw_email.replace('mailto:', ''))
#         wizard_data['personal_info'] = {
#             'first_name': safe_strip(pi.get('First name')),
#             'mid_name': safe_strip(pi.get('Middle name')),
#             'last_name': safe_strip(pi.get('Last name')),
#             'email': cleaned_email,
#             'phone': safe_strip(pi.get('Phone number')),
#             'address': format_location(pi.get('Address')), # Use helper if defined
#             'linkedin': format_url(pi.get('LinkedIn URL')), # Use helper if defined
#             'github': format_url(pi.get('GitHub URL')),     # Use helper if defined
#             'portfolio': format_url(pi.get('Portfolio URL')),# Use helper if defined
#         }
#     else:
#         print("Warning: 'Personal Information' key missing or not a dict in parsed_data.")
#         wizard_data['personal_info'] = {} # Ensure key exists
#
#     # 2. Professional Summary
#     summary_data = parsed_data.get('Professional Summary')
#     # Store as dict consistent with other steps
#     wizard_data['summary'] = {'summary': safe_strip(summary_data)} if isinstance(summary_data, str) else {'summary': ''}
#
#     # 3. Skills
#     wizard_data['skills'] = []
#     raw_skills = parsed_data.get('Skills')
#     if isinstance(raw_skills, list):
#         for skill_data in raw_skills:
#             if isinstance(skill_data, dict):
#                 wizard_data['skills'].append({
#                     'skill_name': safe_strip(skill_data.get('Skill name')),
#                     'skill_type': safe_strip(skill_data.get('Skill type'), 'technical'), # Default type
#                     'proficiency_level': skill_data.get('Estimated proficiency level', 0), # Default proficiency
#                 })
#     elif raw_skills: # Handle case where it might be a string
#         print(f"Warning: 'Skills' data is not a list (type: {type(raw_skills)}). Attempting basic split.")
#         if isinstance(raw_skills, str):
#              for skill_name in raw_skills.split(','): # Basic split
#                  if safe_strip(skill_name):
#                      wizard_data['skills'].append({'skill_name': safe_strip(skill_name), 'skill_type': 'technical', 'proficiency_level': 0})
#
#     # 4. Work Experience
#     wizard_data['experiences'] = []
#     raw_experience = parsed_data.get('Work Experience')
#     if isinstance(raw_experience, list):
#         for exp_data in raw_experience:
#             if isinstance(exp_data, dict):
#                 bullets_raw = exp_data.get('Bullet points', [])
#                 # Format bullets robustly (handle list or string)
#                 formatted_bullets = []
#                 if isinstance(bullets_raw, list):
#                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw if isinstance(b, str) and safe_strip(b)]
#                 elif isinstance(bullets_raw, str):
#                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw.split('\n') if safe_strip(b)]
#
#                 wizard_data['experiences'].append({
#                     'job_title': safe_strip(exp_data.get('Job title')),
#                     'employer': safe_strip(exp_data.get('Employer/Company name')),
#                     'location': format_location(exp_data.get('Location')),
#                     'start_date': format_date(exp_data.get('Start date')), # Use helper
#                     'end_date': format_date(exp_data.get('End date')),     # Use helper
#                     'is_current': exp_data.get('Is current job', False),
#                     'bullet_points': formatted_bullets, # Store as list of dicts
#                 })
#
#     # 5. Education
#     wizard_data['educations'] = []
#     raw_education = parsed_data.get('Education')
#     if isinstance(raw_education, list):
#         for edu_data in raw_education:
#             if isinstance(edu_data, dict):
#                 gpa_val = None
#                 try:
#                     gpa_str = edu_data.get('GPA')
#                     if gpa_str is not None:
#                         # Clean GPA string (remove non-numeric/dot characters)
#                         cleaned_gpa_str = re.sub(r"[^0-9.]", "", str(gpa_str))
#                         # Try converting to float first for session storage, or keep as string
#                         # Using float here matches the previous intent, but string is safer for Decimals
#                         gpa_val = float(cleaned_gpa_str) if cleaned_gpa_str else None
#                 except (ValueError, TypeError):
#                     gpa_val = None # Handle conversion errors
#
#                 wizard_data['educations'].append({
#                     'school_name': safe_strip(edu_data.get('School name')),
#                     'location': format_location(edu_data.get('Location')),
#                     'degree': safe_strip(edu_data.get('Degree')),
#                     'degree_type': safe_strip(edu_data.get('Degree type'), 'bachelor'), # Default
#                     'field_of_study': safe_strip(edu_data.get('Field of study')),
#                     'graduation_date': format_date(edu_data.get('Graduation date')), # Use helper
#                     'gpa': gpa_val, # Store as float or string
#                 })
#
#     # 6. Projects
#     wizard_data['projects'] = []
#     raw_projects = parsed_data.get('Projects')
#     if isinstance(raw_projects, list):
#         for proj_data in raw_projects:
#             if isinstance(proj_data, dict):
#                 bullets_raw = proj_data.get('Bullet points', [])
#                 # Format bullets robustly (handle list or string)
#                 formatted_bullets = []
#                 if isinstance(bullets_raw, list):
#                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw if isinstance(b, str) and safe_strip(b)]
#                 elif isinstance(bullets_raw, str):
#                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw.split('\n') if safe_strip(b)]
#
#                 wizard_data['projects'].append({
#                     'project_name': safe_strip(proj_data.get('Project name')),
#                     'summary': safe_strip(proj_data.get('Summary/description')),
#                     'start_date': format_date(proj_data.get('Start date')), # Use helper
#                     'completion_date': format_date(proj_data.get('Completion date')), # Use helper
#                     'project_link': format_url(proj_data.get('Project URL')), # Use helper
#                     'github_link': format_url(proj_data.get('GitHub URL')),   # Use helper
#                     'bullet_points': formatted_bullets, # Store as list of dicts
#                 })
#
#     # 7. Certifications
#     wizard_data['certifications'] = []
#     raw_certs = parsed_data.get('Certifications')
#     if isinstance(raw_certs, list):
#         for cert_data in raw_certs:
#             if isinstance(cert_data, dict):
#                 wizard_data['certifications'].append({
#                     'name': safe_strip(cert_data.get('Name')),
#                     'institute': safe_strip(cert_data.get('Institute/Issuing organization')),
#                     'completion_date': format_date(cert_data.get('Completion date')), # Use helper
#                     'expiration_date': format_date(cert_data.get('Expiration date')), # Use helper
#                     'score': safe_strip(cert_data.get('Score')),
#                     'link': format_url(cert_data.get('URL/Link')), # Use helper
#                     'description': safe_strip(cert_data.get('Description')),
#                 })
#
#     # 8. Languages
#     wizard_data['languages'] = []
#     raw_langs = parsed_data.get('Languages')
#     if isinstance(raw_langs, list):
#         for lang_data in raw_langs:
#              if isinstance(lang_data, dict):
#                 wizard_data['languages'].append({
#                     'language_name': safe_strip(lang_data.get('Language name')),
#                     'proficiency': safe_strip(lang_data.get('Proficiency'), 'basic'), # Default
#                 })
#
#     # 9. Custom/Additional Sections
#     wizard_data['custom_sections'] = []
#     raw_custom = parsed_data.get('Additional sections') # Check for 'Additional sections' key
#     if isinstance(raw_custom, list):
#         for custom_data in raw_custom:
#             if isinstance(custom_data, dict):
#                 bullets_raw = custom_data.get('Bullet points', [])
#                 # Format bullets as a newline-separated string for CustomData model
#                 formatted_bullets_str = ""
#                 if isinstance(bullets_raw, list):
#                     formatted_bullets_str = "\n".join(f"• {safe_strip(b)}" for b in bullets_raw if isinstance(b, str) and safe_strip(b))
#                 elif isinstance(bullets_raw, str):
#                     lines = [safe_strip(b) for b in bullets_raw.split('\n') if safe_strip(b)]
#                     # Add bullet prefix if not already present
#                     formatted_bullets_str = "\n".join(f"• {line}" if not line.startswith(('•', '*', '-')) else line for line in lines)
#
#                 wizard_data['custom_sections'].append({
#                     'name': safe_strip(custom_data.get('Section name')), # Map key correctly
#                     'completion_date': format_date(custom_data.get('Completion date')), # Use helper
#                     'bullet_points': formatted_bullets_str, # Store as string
#                     'description': safe_strip(custom_data.get('Description')),
#                     'link': format_url(custom_data.get('URL/Link')), # Use helper
#                     'institution_name': safe_strip(custom_data.get('Institution name')),
#                 })
#
#     print("--- Transformation complete ---")
#     # print(json.dumps(wizard_data, indent=2)) # Optional: Print transformed data for debugging
#     return wizard_data
#
# # --- Views ---
#
# @login_required
# def template_selection(request):
#     """Displays template options for the user to select."""
#     print("==== ENTERING template_selection VIEW ====")
#     from_upload = request.session.get('from_resume_upload', False)
#     # Example templates - replace with your actual template data source if needed
#     templates = [
#         {
#             'id': 1, 'name': 'Professional Classic',
#             'description': 'A clean and traditional format, ATS-friendly.',
#             'thumbnail': 'img/templates/1.jpg', # Ensure path is correct relative to static files
#             'tags': ['Classic', 'ATS-Friendly', 'Traditional']
#         },
#         {
#             'id': 2, 'name': 'Modern Minimalist',
#             'description': 'Sleek design focusing on readability and key info.',
#             'thumbnail': 'img/templates/2.jpg',
#             'tags': ['Modern', 'Minimalist', 'Clean']
#         },
#          {
#             'id': 3, 'name': 'Executive Style',
#             'description': 'Elegant and formal, suitable for senior roles.',
#             'thumbnail': 'img/templates/3.jpg',
#             'tags': ['Executive', 'Formal', 'Senior Level']
#         },
#         {
#             'id': 4, 'name': 'Technical Focus',
#             'description': 'Highlights technical skills, projects, and certifications.',
#             'thumbnail': 'img/templates/4.jpg',
#             'tags': ['Technical', 'Skills-Focused', 'IT']
#         },
#         {
#             'id': 5, 'name': 'Clean Professional',
#             'description': 'A modern take on professional resumes with clear sections.',
#             'thumbnail': 'img/templates/5.jpg',
#             'tags': ['Professional', 'Clean', 'Modern']
#         },
#         {
#             'id': 6, 'name': 'Fresh Graduate',
#             'description': 'Emphasizes education, projects, and internships.',
#             'thumbnail': 'img/templates/6.jpg',
#             'tags': ['Entry-Level', 'Academic', 'Internship']
#         },
#         # Add more templates as needed
#     ]
#     is_debug = getattr(settings, 'DEBUG', False)
#     return render(request, 'resumes/template_select.html', {
#         'templates': templates, 'from_upload': from_upload, 'debug': is_debug
#     })
#
#
# @login_required
# @require_http_methods(["POST"])
# def select_template(request):
#     """Handles template selection and initiates the wizard flow."""
#     print("==== ENTERING select_template VIEW (Upload-to-Wizard Flow Enabled) ====")
#     template_id = request.POST.get('template_id')
#     if not template_id:
#         messages.error(request, "Please select a template")
#         return redirect('job_portal:template_selection')
#
#     request.session['resume_template_id'] = template_id
#     from_upload = request.session.get('from_resume_upload', False)
#
#     # Clear previous wizard data if starting anew or from upload
#     request.session['resume_form_data'] = {}
#     request.session['resume_wizard_step'] = 1 # Reset to step 1
#
#     if from_upload:
#         print("Processing uploaded resume data for wizard...")
#         parsed_data_json = request.session.get('parsed_resume_data')
#         if parsed_data_json:
#             try:
#                 parsed_data = json.loads(parsed_data_json)
#                 # Transform data *before* putting it into 'resume_form_data'
#                 transformed_data = transform_parsed_data_to_wizard_format(parsed_data)
#                 request.session['resume_form_data'] = transformed_data # Store transformed data
#                 # Clean up upload-specific session keys
#                 if 'parsed_resume_data' in request.session: del request.session['parsed_resume_data']
#                 if 'from_resume_upload' in request.session: del request.session['from_resume_upload']
#                 if 'resume_ai_engine' in request.session: del request.session['resume_ai_engine']
#                 request.session.modified = True # Ensure session is saved
#                 messages.info(request, "Your uploaded resume data has been loaded. Please review each section.")
#                 return redirect('job_portal:resume_wizard', step=1)
#             except json.JSONDecodeError as json_err:
#                  print(f"ERROR decoding parsed JSON data: {json_err}")
#                  messages.error(request, f"Error loading parsed resume data (invalid format): {json_err}. Please try uploading again.")
#                  return redirect('job_portal:upload_resume')
#             except Exception as e:
#                 print(f"ERROR transforming or processing parsed data: {e}"); traceback.print_exc()
#                 messages.error(request, f"Error processing parsed resume data: {e}. Please try uploading again.")
#                 # Clear potentially corrupted data
#                 if 'parsed_resume_data' in request.session: del request.session['parsed_resume_data']
#                 request.session['resume_form_data'] = {}
#                 request.session.modified = True
#                 return redirect('job_portal:upload_resume')
#         else:
#             messages.error(request, "Parsed resume data not found in session. Please try uploading again.")
#             return redirect('job_portal:upload_resume')
#     else: # Create from Scratch
#         print("Starting wizard from scratch.")
#         # Session data already cleared above
#         request.session.modified = True
#         return redirect('job_portal:resume_wizard', step=1)
#
#
# # --- Wizard View (With Manual Formset Validation Loop - Corrected) ---
# @login_required
#
# def resume_wizard(request, step):
#     """Handle the multi-step form wizard for resume creation."""
#     print(f"\n==== ENTERING resume_wizard VIEW for step {step} ({request.method}) ====")
#     """Handle the multi-step form wizard for resume creation."""
#     print(f"\n==== ENTERING resume_wizard VIEW for step {step} ({request.method}) ====")
#
#     # DEBUGGING CODE - ADD THIS SECTION
#     if request.method == 'POST':
#         print("\n----- DEBUG: POST DATA -----")
#
#         # Print all POST data
#         print("All POST keys:", list(request.POST.keys()))
#
#         # Look specifically for bullet-related fields
#         bullet_keys = [k for k in request.POST.keys() if 'bullet' in k.lower()]
#         print("Bullet-related keys:", bullet_keys)
#
#         for key in bullet_keys:
#             value = request.POST.get(key)
#             print(f"  {key} = {value}")
#
#         # Look for experience-related fields
#         experience_keys = [k for k in request.POST.keys() if 'experience' in k.lower()]
#         print("Experience-related keys:", experience_keys)
#
#         print("----- END DEBUG -----\n")
#
#     template_id = request.session.get('resume_template_id')
#     if not template_id:
#         messages.error(request, "Please select a template first.")
#         return redirect('job_portal:template_selection')
#
#     # Load current wizard data from session
#     form_data = request.session.get('resume_form_data', {})
#     print(f"Session form_data loaded for step {step}: {list(form_data.keys())}")
#
#     # Define Formsets using formset_factory for session data compatibility
#     # Using extra=1 to match the template's expectation for adding new forms
#     SkillFormSet = formset_factory(SkillForm, extra=1, can_delete=True)
#     ExperienceFormSet = formset_factory(ExperienceForm, extra=1, can_delete=True)
#     EducationFormSet = formset_factory(EducationForm, extra=1, can_delete=True)  # Keep extra=1
#     ProjectFormSet = formset_factory(ProjectForm, extra=1, can_delete=True)
#     CertificationFormSet = formset_factory(CertificationForm, extra=1, can_delete=True)
#     LanguageFormSet = formset_factory(LanguageForm, extra=1, can_delete=True)
#     CustomDataFormSet = formset_factory(CustomDataForm, extra=1, can_delete=True)
#
#     # Wizard step configuration
#     steps_config = {
#         1: {'title': 'Personal Information', 'form_class': ResumeBasicInfoForm,
#             'template': 'resumes/wizard_steps/personal_info.html', 'data_key': 'personal_info'},
#         2: {'title': 'Professional Summary', 'form_class': ResumeSummaryForm,
#             'template': 'resumes/wizard_steps/summary.html', 'data_key': 'summary'},
#         3: {'title': 'Skills', 'formset_class': SkillFormSet, 'template': 'resumes/wizard_steps/skills.html',
#             'data_key': 'skills'},
#         4: {'title': 'Work Experience', 'formset_class': ExperienceFormSet,
#             'template': 'resumes/wizard_steps/experience.html', 'data_key': 'experiences'},
#         5: {'title': 'Education', 'formset_class': EducationFormSet, 'template': 'resumes/wizard_steps/education.html',
#             'data_key': 'educations'},
#         6: {'title': 'Projects', 'formset_class': ProjectFormSet, 'template': 'resumes/wizard_steps/projects.html',
#             'data_key': 'projects'},
#         7: {'title': 'Certifications', 'formset_class': CertificationFormSet,
#             'template': 'resumes/wizard_steps/certifications.html', 'data_key': 'certifications'},
#         8: {'title': 'Languages', 'formset_class': LanguageFormSet, 'template': 'resumes/wizard_steps/languages.html',
#             'data_key': 'languages'},
#         9: {'title': 'Additional Sections', 'formset_class': CustomDataFormSet,
#             'template': 'resumes/wizard_steps/custom_sections.html', 'data_key': 'custom_sections'},
#     }
#
#     # Validate step number
#     try:
#         step = int(step)
#         if step < 1 or step > len(steps_config):
#             print(f"Invalid step number ({step}). Redirecting to step 1.")
#             return redirect('job_portal:resume_wizard', step=1)
#     except ValueError:
#         print(f"Invalid step value ('{step}'). Redirecting to step 1.")
#         return redirect('job_portal:resume_wizard', step=1)
#
#     # Update current step in session
#     request.session['resume_wizard_step'] = step
#     step_info = steps_config[step]
#     data_key = step_info['data_key']
#     template_name = step_info['template']
#     form = None  # To hold the form instance if step uses a single form
#     formset = None  # To hold the formset instance if step uses a formset
#
#     # --- POST Request Handling ---
#     if request.method == 'POST':
#         print(f"Processing POST for step {step} ('{data_key}')")
#         is_valid_overall = True  # Assume valid initially for the whole step
#
#         # --- Single Form Steps (1, 2) ---
#         if step_info.get('form_class'):
#             form = step_info['form_class'](request.POST)
#             if form.is_valid():
#                 cleaned_data = form.cleaned_data.copy()
#                 # Convert dates AND Decimals to strings for session serialization
#                 for field, value in cleaned_data.items():
#                     if isinstance(value, date):
#                         cleaned_data[field] = value.strftime('%Y-%m-%d')
#                     elif isinstance(value, Decimal):  # Handle potential Decimals
#                         cleaned_data[field] = str(value)
#                 form_data[data_key] = cleaned_data  # Update session data
#                 print(f"Step {step} form is valid. Data updated.")
#             else:
#                 print(f"Form errors step {step}: {form.errors.as_json()}")
#                 messages.error(request, f"Please correct the errors in the '{step_info['title']}' section.")
#                 is_valid_overall = False
#
#         # --- Formset Steps (3-9) ---
#         elif step_info.get('formset_class'):
#             prefix = f'step{step}_{data_key}'  # Unique prefix for the formset
#             CurrentFormSet = step_info['formset_class']
#             formset = CurrentFormSet(request.POST, prefix=prefix)
#
#             # --- Manual Validation Loop for Formsets ---
#             cleaned_data_list = []
#             any_form_errors = False  # Flag to check if any form has errors
#
#             # Check management form validity FIRST using the correct attribute
#             if not formset.management_form.is_valid():
#                 print(f"Management form errors step {step}: {formset.management_form.errors}")
#                 messages.error(request,
#                                f"There was a problem processing the {step_info['title']} section structure. Please try again.")
#                 is_valid_overall = False
#             else:
#                 # Iterate through each form in the formset
#                 for form_instance in formset.forms:
#                     # 1. Skip forms marked for deletion (check POST directly)
#                     delete_key = f'{form_instance.prefix}-DELETE'
#                     if formset.can_delete and request.POST.get(delete_key):
#                         print(f"  Skipping deleted form (POST check): {form_instance.prefix}")
#                         continue  # Move to the next form
#
#                     # 2. Validate this specific form IF it wasn't marked for deletion
#                     print(f"  Checking form: {form_instance.prefix}")
#                     if form_instance.is_valid():
#                         # 3. Now check if it actually changed (to skip blank extra forms that passed validation)
#                         if not form_instance.has_changed():
#                             print(f"  Skipping unchanged valid form: {form_instance.prefix}")
#                             continue  # Move to the next form
#
#                         # 4. Process valid, changed, non-deleted forms
#                         print(f"  Processing valid, changed form: {form_instance.prefix}")
#                         form_instance_data = form_instance.cleaned_data
#                         if not form_instance_data: continue  # Safeguard
#
#                         entry_data = form_instance_data.copy()
#                         entry_data.pop('DELETE', None)  # Ensure DELETE is removed
#
#                         # Convert dates AND Decimals to strings for session serialization
#                         for field, value in entry_data.items():
#                             if isinstance(value, date):
#                                 entry_data[field] = value.strftime('%Y-%m-%d')
#                             # Fix for the TypeError
#                             elif isinstance(value, Decimal):
#                                 entry_data[field] = str(value)  # Convert Decimal to string
#
#                         # --- Handle Bullet Points Manually --- [THIS IS THE FIXED CODE]
#                         if data_key in ['experiences', 'projects', 'custom_sections']:
#                             current_bullets = []
#                             form_prefix = form_instance.prefix
#                             match = re.search(r'-(\d+)$', form_prefix)
#                             if match:
#                                 form_index = int(match.group(1))
#                                 bullet_index = 0
#
#                                 # Bullet name pattern - this is the critical fix
#                                 # Looking for bullet_0_0, bullet_0_1, etc. as in your HTML templates
#                                 bullet_name_pattern = f'bullet_{form_index}_'
#                                 print(f"    Looking for bullets with pattern: {bullet_name_pattern}*")
#
#                                 # Now look for bullets with this pattern
#                                 while True:
#                                     bullet_field_name = f'{bullet_name_pattern}{bullet_index}'
#                                     bullet_value = request.POST.get(bullet_field_name)
#
#                                     if bullet_value is None:
#                                         if bullet_index == 0:
#                                             print(f"    No bullets found with pattern: {bullet_name_pattern}*")
#                                         break  # Stop searching
#
#                                     if bullet_value and bullet_value.strip():
#                                         print(f"    Found bullet '{bullet_field_name}': {bullet_value[:30]}...")
#                                         if data_key in ['experiences', 'projects']:
#                                             current_bullets.append({'description': bullet_value.strip()})
#                                         elif data_key == 'custom_sections':
#                                             bullet_line = bullet_value.strip()
#                                             if not bullet_line.startswith(('•', '*', '-')):
#                                                 current_bullets.append(f"• {bullet_line}")
#                                             else:
#                                                 current_bullets.append(bullet_line)
#                                     else:
#                                         print(f"    Skipping empty bullet: {bullet_field_name}")
#
#                                     bullet_index += 1
#
#                                 # Assign collected bullets
#                                 if data_key in ['experiences', 'projects']:
#                                     entry_data['bullet_points'] = current_bullets
#                                     print(f"    Collected {len(current_bullets)} bullets for {form_prefix}")
#                                 elif data_key == 'custom_sections':
#                                     entry_data['bullet_points'] = "\n".join(current_bullets)  # Join for custom section
#                                     print(f"    Collected {len(current_bullets)} bullet lines for {form_prefix}")
#                             else:
#                                 print(
#                                     f"Warning: Could not extract index from form prefix '{form_prefix}' for bullet handling.")
#                                 # Assign empty based on expected type
#                                 entry_data['bullet_points'] = [] if data_key != 'custom_sections' else ""
#
#                         # Add the processed data for this form instance to the list
#                         cleaned_data_list.append(entry_data)
#
#                     else:  # This specific form is invalid
#                         print(
#                             f"  Individual form {form_instance.prefix} is invalid. Errors: {form_instance.errors.as_json()}")
#                         is_valid_overall = False  # Mark the whole step as invalid
#                         any_form_errors = True  # Flag that we found errors
#
#                 # After iterating through all forms, check for non-form errors
#                 if formset.non_form_errors():
#                     print(f"Non-form errors step {step}: {formset.non_form_errors()}")
#                     messages.error(request,
#                                    f"There was a problem processing the {step_info['title']} section structure (non-form errors). Please try again.")
#                     is_valid_overall = False
#
#             # Display general error message if any form had issues
#             if any_form_errors:
#                 messages.error(request, f"Please correct the errors highlighted in the '{step_info['title']}' section.")
#                 # is_valid_overall is already False
#
#             # Save data to session *only if* the entire step processing was valid
#             if is_valid_overall:
#                 form_data[data_key] = cleaned_data_list
#                 print(
#                     f"Step {step} formset processing complete. Saved {len(cleaned_data_list)} valid entries to session for key '{data_key}'.")
#             else:
#                 print(f"Step {step} formset is invalid overall. Not updating session data for '{data_key}'.")
#
#         # --- Navigation Logic ---
#         if is_valid_overall:
#             # Save the updated form_data to the session
#             request.session['resume_form_data'] = form_data
#             request.session.modified = True  # Crucial: ensure session is saved
#             print(f"Session data saved for step {step}.")
#
#             # Determine next step or completion
#             next_step = step + 1
#             if next_step > len(steps_config):
#                 print(f"Finished final step {step}. Redirecting to generate resume.")
#                 # Optionally clear wizard step tracker
#                 # request.session.pop('resume_wizard_step', None)
#                 # Make sure you have a URL named 'generate_resume' or change this redirect
#                 return redirect('job_portal:generate_resume')  # Replace if needed
#             else:
#                 print(f"Redirecting to step {next_step}")
#                 return redirect('job_portal:resume_wizard', step=next_step)
#         else:
#             # If not valid, fall through to GET logic below to re-render the current step with errors
#             print(f"Step {step} validation failed. Re-rendering template.")
#             pass  # Fall through
#
#     # --- GET Request Handling (or Invalid POST) ---
#     print(f"Handling GET request or re-rendering after invalid POST for step {step}")
#     context = {
#         'step': step,
#         'total_steps': len(steps_config),
#         'step_title': step_info['title'],
#         'template_id': template_id,
#         'previous_step': step - 1 if step > 1 else None,
#         'next_step': step + 1 if step < len(steps_config) else None,  # For navigation buttons
#         'is_final_step': step == len(steps_config),
#     }
#
#     # Add skills data when on the experiences step (for potential JS interaction)
#     if step == 4:  # Experience step
#         skills_data = form_data.get('skills', [])
#         try:
#             # Ensure data is serializable for template context
#             skills_json = json.dumps(skills_data)
#             context['skills_data'] = skills_json
#         except TypeError as e:
#             print(f"Warning: Could not serialize skills data for context: {e}")
#             context['skills_data'] = '[]'  # Fallback to empty JSON array string
#
#     # Initialize form or formset for rendering
#     if step_info.get('form_class'):  # Steps 1, 2
#         # If POST failed, use the invalid form instance to show errors
#         form_to_render = form if (request.method == 'POST' and form and not is_valid_overall) else None
#         if not form_to_render:
#             # Get initial data from session for GET request
#             initial_data = form_data.get(data_key, {})
#             # Ensure data structure is correct (e.g., summary needs {'summary': ...})
#             if step == 2:
#                 if isinstance(initial_data, str):
#                     initial_data = {'summary': initial_data}
#                 elif not isinstance(initial_data, dict):
#                     initial_data = {'summary': ''}
#             elif step == 1 and not isinstance(initial_data, dict):
#                 initial_data = {}  # Ensure dict for personal info
#
#             form_to_render = step_info['form_class'](initial=initial_data)
#             print(f"  Initialized form for GET with initial data keys: {list(initial_data.keys())}")
#         else:
#             print("  Rendering form instance from invalid POST.")
#         context['form'] = form_to_render
#
#     elif step_info.get('formset_class'):  # Steps 3-9
#         # If POST failed, use the invalid formset instance to show errors
#         formset_to_render = formset if (request.method == 'POST' and formset and not is_valid_overall) else None
#         if not formset_to_render:
#             # Get initial data list from session for GET request
#             prefix = f'step{step}_{data_key}'  # Prefix must match POST
#             initial_list = form_data.get(data_key, [])
#             if not isinstance(initial_list, list):
#                 print(f"  Warning: Initial data for step {step} ('{data_key}') is not a list. Resetting.")
#                 initial_list = []
#
#             print(
#                 f"  Initializing formset for GET. Key: '{data_key}', Prefix: '{prefix}', Initial items: {len(initial_list)}")
#             # print(f"  Initial data sample: {initial_list[:2]}") # Print sample if list is long
#
#             CurrentFormSet = step_info['formset_class']
#             formset_to_render = CurrentFormSet(initial=initial_list, prefix=prefix)
#         else:
#             print("  Rendering formset instance from invalid POST.")
#         context['formset'] = formset_to_render
#
#         # Pass any choices needed by the specific step's template
#         if step == 3: context['skill_types'] = dict(Skill.SKILL_TYPES)
#         if step == 5: context['degree_types'] = dict(Education.DEGREE_TYPES)
#         if step == 8: context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
#         # Add context for other steps if needed
#
#     print(f"Rendering template: {template_name} for step {step}")
#     return render(request, template_name, context)
# # def resume_wizard(request, step):
# #     """Handle the multi-step form wizard for resume creation."""
# #     print(f"\n==== ENTERING resume_wizard VIEW for step {step} ({request.method}) ====")
# #
# #     template_id = request.session.get('resume_template_id')
# #     if not template_id:
# #         messages.error(request, "Please select a template first.")
# #         return redirect('job_portal:template_selection')
# #
# #     # Load current wizard data from session
# #     form_data = request.session.get('resume_form_data', {})
# #     print(f"Session form_data loaded for step {step}: {list(form_data.keys())}")
# #
# #     # Define Formsets using formset_factory for session data compatibility
# #     # Using extra=1 to match the template's expectation for adding new forms
# #     SkillFormSet = formset_factory(SkillForm, extra=1, can_delete=True)
# #     ExperienceFormSet = formset_factory(ExperienceForm, extra=1, can_delete=True)
# #     EducationFormSet = formset_factory(EducationForm, extra=1, can_delete=True) # Keep extra=1
# #     ProjectFormSet = formset_factory(ProjectForm, extra=1, can_delete=True)
# #     CertificationFormSet = formset_factory(CertificationForm, extra=1, can_delete=True)
# #     LanguageFormSet = formset_factory(LanguageForm, extra=1, can_delete=True)
# #     CustomDataFormSet = formset_factory(CustomDataForm, extra=1, can_delete=True)
# #
# #     # Wizard step configuration
# #     steps_config = {
# #         1: {'title': 'Personal Information', 'form_class': ResumeBasicInfoForm, 'template': 'resumes/wizard_steps/personal_info.html', 'data_key': 'personal_info'},
# #         2: {'title': 'Professional Summary', 'form_class': ResumeSummaryForm, 'template': 'resumes/wizard_steps/summary.html', 'data_key': 'summary'},
# #         3: {'title': 'Skills', 'formset_class': SkillFormSet, 'template': 'resumes/wizard_steps/skills.html', 'data_key': 'skills'},
# #         4: {'title': 'Work Experience', 'formset_class': ExperienceFormSet, 'template': 'resumes/wizard_steps/experience.html', 'data_key': 'experiences'},
# #         5: {'title': 'Education', 'formset_class': EducationFormSet, 'template': 'resumes/wizard_steps/education.html', 'data_key': 'educations'},
# #         6: {'title': 'Projects', 'formset_class': ProjectFormSet, 'template': 'resumes/wizard_steps/projects.html', 'data_key': 'projects'},
# #         7: {'title': 'Certifications', 'formset_class': CertificationFormSet, 'template': 'resumes/wizard_steps/certifications.html', 'data_key': 'certifications'},
# #         8: {'title': 'Languages', 'formset_class': LanguageFormSet, 'template': 'resumes/wizard_steps/languages.html', 'data_key': 'languages'},
# #         9: {'title': 'Additional Sections', 'formset_class': CustomDataFormSet, 'template': 'resumes/wizard_steps/custom_sections.html', 'data_key': 'custom_sections'},
# #     }
# #
# #     # Validate step number
# #     try:
# #         step = int(step)
# #         if step < 1 or step > len(steps_config):
# #             print(f"Invalid step number ({step}). Redirecting to step 1.")
# #             return redirect('job_portal:resume_wizard', step=1)
# #     except ValueError:
# #         print(f"Invalid step value ('{step}'). Redirecting to step 1.")
# #         return redirect('job_portal:resume_wizard', step=1)
# #
# #     # Update current step in session
# #     request.session['resume_wizard_step'] = step
# #     step_info = steps_config[step]
# #     data_key = step_info['data_key']
# #     template_name = step_info['template']
# #     form = None       # To hold the form instance if step uses a single form
# #     formset = None    # To hold the formset instance if step uses a formset
# #
# #     # --- POST Request Handling ---
# #     if request.method == 'POST':
# #         print(f"Processing POST for step {step} ('{data_key}')")
# #         is_valid_overall = True # Assume valid initially for the whole step
# #
# #         # --- Single Form Steps (1, 2) ---
# #         if step_info.get('form_class'):
# #             form = step_info['form_class'](request.POST)
# #             if form.is_valid():
# #                 cleaned_data = form.cleaned_data.copy()
# #                 # Convert dates AND Decimals to strings for session serialization
# #                 # (Decimals less likely here, but good practice)
# #                 for field, value in cleaned_data.items():
# #                     if isinstance(value, date):
# #                         cleaned_data[field] = value.strftime('%Y-%m-%d')
# #                     elif isinstance(value, Decimal): # Handle potential Decimals
# #                         cleaned_data[field] = str(value)
# #                 form_data[data_key] = cleaned_data # Update session data
# #                 print(f"Step {step} form is valid. Data updated.")
# #             else:
# #                 print(f"Form errors step {step}: {form.errors.as_json()}")
# #                 messages.error(request, f"Please correct the errors in the '{step_info['title']}' section.")
# #                 is_valid_overall = False
# #
# #         # --- Formset Steps (3-9) ---
# #         elif step_info.get('formset_class'):
# #             prefix = f'step{step}_{data_key}' # Unique prefix for the formset
# #             CurrentFormSet = step_info['formset_class']
# #             formset = CurrentFormSet(request.POST, prefix=prefix)
# #
# #             # --- Manual Validation Loop for Formsets ---
# #             cleaned_data_list = []
# #             any_form_errors = False # Flag to check if any form has errors
# #
# #             # Check management form validity FIRST using the correct attribute
# #             if not formset.management_form.is_valid():
# #                  print(f"Management form errors step {step}: {formset.management_form.errors}")
# #                  messages.error(request, f"There was a problem processing the {step_info['title']} section structure. Please try again.")
# #                  is_valid_overall = False
# #             else:
# #                 # Iterate through each form in the formset
# #                 for form_instance in formset.forms:
# #                     # 1. Skip forms marked for deletion (check POST directly)
# #                     delete_key = f'{form_instance.prefix}-DELETE'
# #                     if formset.can_delete and request.POST.get(delete_key):
# #                         print(f"  Skipping deleted form (POST check): {form_instance.prefix}")
# #                         continue # Move to the next form
# #
# #                     # 2. Validate this specific form IF it wasn't marked for deletion
# #                     print(f"  Checking form: {form_instance.prefix}")
# #                     if form_instance.is_valid():
# #                         # 3. Now check if it actually changed (to skip blank extra forms that passed validation)
# #                         if not form_instance.has_changed():
# #                             print(f"  Skipping unchanged valid form: {form_instance.prefix}")
# #                             continue # Move to the next form
# #
# #                         # 4. Process valid, changed, non-deleted forms
# #                         print(f"  Processing valid, changed form: {form_instance.prefix}")
# #                         form_instance_data = form_instance.cleaned_data
# #                         if not form_instance_data: continue # Safeguard
# #
# #                         entry_data = form_instance_data.copy()
# #                         entry_data.pop('DELETE', None) # Ensure DELETE is removed
# #
# #                         # Convert dates AND Decimals to strings for session serialization
# #                         for field, value in entry_data.items():
# #                             if isinstance(value, date):
# #                                 entry_data[field] = value.strftime('%Y-%m-%d')
# #                             # *** THIS IS THE FIX for the TypeError ***
# #                             elif isinstance(value, Decimal):
# #                                 entry_data[field] = str(value) # Convert Decimal to string
# #                             # ****************************************
# #
# #                         # --- Handle Bullet Points Manually ---
# #                         if data_key in ['experiences', 'projects', 'custom_sections']:
# #                             current_bullets = []
# #                             form_prefix = form_instance.prefix
# #                             match = re.search(r'-(\d+)$', form_prefix)
# #                             if match:
# #                                 form_index = int(match.group(1))
# #                                 bullet_index = 0
# #                                 # *** USE CORRECTED NAME PATTERN ***
# #                                 bullet_name_pattern = f'bullet_{form_index}_' # Check if this matches your template
# #                                 # **********************************
# #                                 print(f"    Looking for bullets with pattern: {bullet_name_pattern}*") # Debug print
# #
# #                                 while True:
# #                                     bullet_field_name = f'{bullet_name_pattern}{bullet_index}'
# #                                     bullet_value = request.POST.get(bullet_field_name)
# #
# #                                     if bullet_value is None:
# #                                         if bullet_index == 0: # Log only if first bullet isn't found
# #                                              print(f"    Bullet field '{bullet_name_pattern}0' not found for {form_prefix}. Assuming no bullets or check template naming.")
# #                                         break # Stop searching
# #
# #                                     if bullet_value.strip():
# #                                         print(f"    Found bullet '{bullet_field_name}': {bullet_value[:30]}...")
# #                                         if data_key in ['experiences', 'projects']:
# #                                             current_bullets.append({'description': bullet_value.strip()})
# #                                         elif data_key == 'custom_sections':
# #                                             bullet_line = bullet_value.strip()
# #                                             # Add bullet prefix if not already present and is custom section
# #                                             if not bullet_line.startswith(('•', '*', '-')):
# #                                                 current_bullets.append(f"• {bullet_line}")
# #                                             else:
# #                                                 current_bullets.append(bullet_line)
# #                                     else:
# #                                         print(f"    Skipping empty bullet: {bullet_field_name}")
# #                                     bullet_index += 1
# #
# #                                 # Assign collected bullets
# #                                 if data_key in ['experiences', 'projects']:
# #                                     entry_data['bullet_points'] = current_bullets
# #                                     print(f"    Collected {len(current_bullets)} bullets for {form_prefix}")
# #                                 elif data_key == 'custom_sections':
# #                                      entry_data['bullet_points'] = "\n".join(current_bullets) # Join for custom section
# #                                      print(f"    Collected {len(current_bullets)} bullet lines for {form_prefix}")
# #                             else:
# #                                 print(f"Warning: Could not extract index from form prefix '{form_prefix}' for bullet handling.")
# #                                 # Assign empty based on expected type
# #                                 entry_data['bullet_points'] = [] if data_key != 'custom_sections' else ""
# #
# #                         # Add the processed data for this form instance to the list
# #                         cleaned_data_list.append(entry_data)
# #
# #                     else: # This specific form is invalid
# #                         print(f"  Individual form {form_instance.prefix} is invalid. Errors: {form_instance.errors.as_json()}")
# #                         is_valid_overall = False # Mark the whole step as invalid
# #                         any_form_errors = True # Flag that we found errors
# #
# #
# #                 # After iterating through all forms, check for non-form errors
# #                 if formset.non_form_errors():
# #                     print(f"Non-form errors step {step}: {formset.non_form_errors()}")
# #                     messages.error(request, f"There was a problem processing the {step_info['title']} section structure (non-form errors). Please try again.")
# #                     is_valid_overall = False
# #
# #             # Display general error message if any form had issues
# #             if any_form_errors:
# #                 messages.error(request, f"Please correct the errors highlighted in the '{step_info['title']}' section.")
# #                 # is_valid_overall is already False
# #
# #             # Save data to session *only if* the entire step processing was valid
# #             if is_valid_overall:
# #                 form_data[data_key] = cleaned_data_list
# #                 print(f"Step {step} formset processing complete. Saved {len(cleaned_data_list)} valid entries to session for key '{data_key}'.")
# #             else:
# #                  print(f"Step {step} formset is invalid overall. Not updating session data for '{data_key}'.")
# #
# #
# #         # --- Navigation Logic ---
# #         if is_valid_overall:
# #             # Save the updated form_data to the session
# #             request.session['resume_form_data'] = form_data
# #             request.session.modified = True # Crucial: ensure session is saved
# #             print(f"Session data saved for step {step}.")
# #
# #             # Determine next step or completion
# #             next_step = step + 1
# #             if next_step > len(steps_config):
# #                 print(f"Finished final step {step}. Redirecting to generate resume.")
# #                 # Optionally clear wizard step tracker
# #                 # request.session.pop('resume_wizard_step', None)
# #                 # Make sure you have a URL named 'generate_resume' or change this redirect
# #                 return redirect('job_portal:generate_resume') # Replace if needed
# #             else:
# #                 print(f"Redirecting to step {next_step}")
# #                 return redirect('job_portal:resume_wizard', step=next_step)
# #         else:
# #             # If not valid, fall through to GET logic below to re-render the current step with errors
# #             print(f"Step {step} validation failed. Re-rendering template.")
# #             pass # Fall through
# #
# #     # --- GET Request Handling (or Invalid POST) ---
# #     print(f"Handling GET request or re-rendering after invalid POST for step {step}")
# #     context = {
# #         'step': step,
# #         'total_steps': len(steps_config),
# #         'step_title': step_info['title'],
# #         'template_id': template_id,
# #         'previous_step': step - 1 if step > 1 else None,
# #         'next_step': step + 1 if step < len(steps_config) else None, # For navigation buttons
# #         'is_final_step': step == len(steps_config),
# #     }
# #
# #     # Add skills data when on the experiences step (for potential JS interaction)
# #     if step == 4:  # Experience step
# #         skills_data = form_data.get('skills', [])
# #         try:
# #             # Ensure data is serializable for template context
# #             skills_json = json.dumps(skills_data)
# #             context['skills_data'] = skills_json
# #         except TypeError as e:
# #             print(f"Warning: Could not serialize skills data for context: {e}")
# #             context['skills_data'] = '[]' # Fallback to empty JSON array string
# #
# #     # Initialize form or formset for rendering
# #     if step_info.get('form_class'): # Steps 1, 2
# #         # If POST failed, use the invalid form instance to show errors
# #         form_to_render = form if (request.method == 'POST' and form and not is_valid_overall) else None
# #         if not form_to_render:
# #             # Get initial data from session for GET request
# #             initial_data = form_data.get(data_key, {})
# #             # Ensure data structure is correct (e.g., summary needs {'summary': ...})
# #             if step == 2:
# #                 if isinstance(initial_data, str): initial_data = {'summary': initial_data}
# #                 elif not isinstance(initial_data, dict): initial_data = {'summary': ''}
# #             elif step == 1 and not isinstance(initial_data, dict): initial_data = {} # Ensure dict for personal info
# #
# #             form_to_render = step_info['form_class'](initial=initial_data)
# #             print(f"  Initialized form for GET with initial data keys: {list(initial_data.keys())}")
# #         else:
# #              print("  Rendering form instance from invalid POST.")
# #         context['form'] = form_to_render
# #
# #     elif step_info.get('formset_class'): # Steps 3-9
# #         # If POST failed, use the invalid formset instance to show errors
# #         formset_to_render = formset if (request.method == 'POST' and formset and not is_valid_overall) else None
# #         if not formset_to_render:
# #             # Get initial data list from session for GET request
# #             prefix = f'step{step}_{data_key}' # Prefix must match POST
# #             initial_list = form_data.get(data_key, [])
# #             if not isinstance(initial_list, list):
# #                 print(f"  Warning: Initial data for step {step} ('{data_key}') is not a list. Resetting.")
# #                 initial_list = []
# #
# #             print(f"  Initializing formset for GET. Key: '{data_key}', Prefix: '{prefix}', Initial items: {len(initial_list)}")
# #             # print(f"  Initial data sample: {initial_list[:2]}") # Print sample if list is long
# #
# #             CurrentFormSet = step_info['formset_class']
# #             formset_to_render = CurrentFormSet(initial=initial_list, prefix=prefix)
# #         else:
# #              print("  Rendering formset instance from invalid POST.")
# #         context['formset'] = formset_to_render
# #
# #         # Pass any choices needed by the specific step's template
# #         if step == 3: context['skill_types'] = dict(Skill.SKILL_TYPES)
# #         if step == 5: context['degree_types'] = dict(Education.DEGREE_TYPES)
# #         if step == 8: context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
# #         # Add context for other steps if needed
# #
# #     print(f"Rendering template: {template_name} for step {step}")
# #     return render(request, template_name, context)
#
# # Note: Ensure you have a URL pattern named 'generate_resume' in your urls.py
# # pointing to a view that handles the final resume generation/display.
#
#
# # # job_portal/views/template_selection_view.py
# #
# # import json
# # import re
# # import traceback
# # from datetime import date
# #
# # from django.conf import settings
# # from django.contrib import messages
# # from django.contrib.auth.decorators import login_required
# # # Import BaseFormSet, BaseModelFormSet - Not strictly needed here, but good practice
# # from django.forms import formset_factory
# # from django.shortcuts import render, redirect
# # from django.views.decorators.http import require_http_methods
# #
# # # Import necessary forms and models
# # from ..forms.resume_creation_form import (
# #     ResumeBasicInfoForm, ResumeSummaryForm, ExperienceForm,
# #     EducationForm, SkillForm, ProjectForm, CertificationForm, LanguageForm, CustomDataForm,
# # )
# # from ..models import (
# #     Skill, Education, Language
# # )
# #
# # # Import helper functions from resume_parser_service
# # try:
# #     from services.resume_parser_service import format_date, format_url, format_location, safe_strip
# # except ImportError:
# #     print("Warning: Could not import helper functions from services.resume_parser_service.")
# #     # Define fallback functions if import fails
# #     def safe_strip(value, default=''): return value.strip() if isinstance(value, str) else default
# #     def format_date(d):
# #         # Add basic date handling if needed, otherwise just return
# #         return d
# #     def format_url(u):
# #         # Add basic URL handling if needed, otherwise just return
# #         return u
# #     def format_location(l):
# #         # Add basic location handling if needed, otherwise just return
# #         return l if isinstance(l, str) else ""
# #
# #
# # # --- transform_parsed_data_to_wizard_format ---
# # def transform_parsed_data_to_wizard_format(parsed_data):
# #     """Transforms parsed resume data (dict) into the format expected by the wizard's session data."""
# #     print("--- Transforming parsed data to wizard format ---")
# #     wizard_data = {}
# #     if not isinstance(parsed_data, dict):
# #         print(f"Error: parsed_data is not a dictionary (type: {type(parsed_data)}). Returning empty.")
# #         return {}
# #
# #     # 1. Personal Information
# #     pi = parsed_data.get('Personal Information', {})
# #     if isinstance(pi, dict):
# #         raw_email = pi.get('Email')
# #         cleaned_email = None
# #         if isinstance(raw_email, str):
# #             # Remove mailto: prefix and strip whitespace
# #             cleaned_email = safe_strip(raw_email.replace('mailto:', ''))
# #         wizard_data['personal_info'] = {
# #             'first_name': safe_strip(pi.get('First name')),
# #             'mid_name': safe_strip(pi.get('Middle name')),
# #             'last_name': safe_strip(pi.get('Last name')),
# #             'email': cleaned_email,
# #             'phone': safe_strip(pi.get('Phone number')),
# #             'address': format_location(pi.get('Address')), # Use helper if defined
# #             'linkedin': format_url(pi.get('LinkedIn URL')), # Use helper if defined
# #             'github': format_url(pi.get('GitHub URL')),     # Use helper if defined
# #             'portfolio': format_url(pi.get('Portfolio URL')),# Use helper if defined
# #         }
# #     else:
# #         print("Warning: 'Personal Information' key missing or not a dict in parsed_data.")
# #         wizard_data['personal_info'] = {} # Ensure key exists
# #
# #     # 2. Professional Summary
# #     summary_data = parsed_data.get('Professional Summary')
# #     # Store as dict consistent with other steps
# #     wizard_data['summary'] = {'summary': safe_strip(summary_data)} if isinstance(summary_data, str) else {'summary': ''}
# #
# #     # 3. Skills
# #     wizard_data['skills'] = []
# #     raw_skills = parsed_data.get('Skills')
# #     if isinstance(raw_skills, list):
# #         for skill_data in raw_skills:
# #             if isinstance(skill_data, dict):
# #                 wizard_data['skills'].append({
# #                     'skill_name': safe_strip(skill_data.get('Skill name')),
# #                     'skill_type': safe_strip(skill_data.get('Skill type'), 'technical'), # Default type
# #                     'proficiency_level': skill_data.get('Estimated proficiency level', 0), # Default proficiency
# #                 })
# #     elif raw_skills: # Handle case where it might be a string
# #         print(f"Warning: 'Skills' data is not a list (type: {type(raw_skills)}). Attempting basic split.")
# #         if isinstance(raw_skills, str):
# #              for skill_name in raw_skills.split(','): # Basic split
# #                  if safe_strip(skill_name):
# #                      wizard_data['skills'].append({'skill_name': safe_strip(skill_name), 'skill_type': 'technical', 'proficiency_level': 0})
# #
# #     # 4. Work Experience
# #     wizard_data['experiences'] = []
# #     raw_experience = parsed_data.get('Work Experience')
# #     if isinstance(raw_experience, list):
# #         for exp_data in raw_experience:
# #             if isinstance(exp_data, dict):
# #                 bullets_raw = exp_data.get('Bullet points', [])
# #                 # Format bullets robustly (handle list or string)
# #                 formatted_bullets = []
# #                 if isinstance(bullets_raw, list):
# #                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw if isinstance(b, str) and safe_strip(b)]
# #                 elif isinstance(bullets_raw, str):
# #                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw.split('\n') if safe_strip(b)]
# #
# #                 wizard_data['experiences'].append({
# #                     'job_title': safe_strip(exp_data.get('Job title')),
# #                     'employer': safe_strip(exp_data.get('Employer/Company name')),
# #                     'location': format_location(exp_data.get('Location')),
# #                     'start_date': format_date(exp_data.get('Start date')), # Use helper
# #                     'end_date': format_date(exp_data.get('End date')),     # Use helper
# #                     'is_current': exp_data.get('Is current job', False),
# #                     'bullet_points': formatted_bullets, # Store as list of dicts
# #                 })
# #
# #     # 5. Education
# #     wizard_data['educations'] = []
# #     raw_education = parsed_data.get('Education')
# #     if isinstance(raw_education, list):
# #         for edu_data in raw_education:
# #             if isinstance(edu_data, dict):
# #                 gpa_val = None
# #                 try:
# #                     gpa_str = edu_data.get('GPA')
# #                     if gpa_str is not None:
# #                         # Clean GPA string (remove non-numeric/dot characters)
# #                         cleaned_gpa_str = re.sub(r"[^0-9.]", "", str(gpa_str))
# #                         gpa_val = float(cleaned_gpa_str) if cleaned_gpa_str else None
# #                 except (ValueError, TypeError):
# #                     gpa_val = None # Handle conversion errors
# #
# #                 wizard_data['educations'].append({
# #                     'school_name': safe_strip(edu_data.get('School name')),
# #                     'location': format_location(edu_data.get('Location')),
# #                     'degree': safe_strip(edu_data.get('Degree')),
# #                     'degree_type': safe_strip(edu_data.get('Degree type'), 'bachelor'), # Default
# #                     'field_of_study': safe_strip(edu_data.get('Field of study')),
# #                     'graduation_date': format_date(edu_data.get('Graduation date')), # Use helper
# #                     'gpa': gpa_val,
# #                 })
# #
# #     # 6. Projects
# #     wizard_data['projects'] = []
# #     raw_projects = parsed_data.get('Projects')
# #     if isinstance(raw_projects, list):
# #         for proj_data in raw_projects:
# #             if isinstance(proj_data, dict):
# #                 bullets_raw = proj_data.get('Bullet points', [])
# #                 # Format bullets robustly (handle list or string)
# #                 formatted_bullets = []
# #                 if isinstance(bullets_raw, list):
# #                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw if isinstance(b, str) and safe_strip(b)]
# #                 elif isinstance(bullets_raw, str):
# #                     formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw.split('\n') if safe_strip(b)]
# #
# #                 wizard_data['projects'].append({
# #                     'project_name': safe_strip(proj_data.get('Project name')),
# #                     'summary': safe_strip(proj_data.get('Summary/description')),
# #                     'start_date': format_date(proj_data.get('Start date')), # Use helper
# #                     'completion_date': format_date(proj_data.get('Completion date')), # Use helper
# #                     'project_link': format_url(proj_data.get('Project URL')), # Use helper
# #                     'github_link': format_url(proj_data.get('GitHub URL')),   # Use helper
# #                     'bullet_points': formatted_bullets, # Store as list of dicts
# #                 })
# #
# #     # 7. Certifications
# #     wizard_data['certifications'] = []
# #     raw_certs = parsed_data.get('Certifications')
# #     if isinstance(raw_certs, list):
# #         for cert_data in raw_certs:
# #             if isinstance(cert_data, dict):
# #                 wizard_data['certifications'].append({
# #                     'name': safe_strip(cert_data.get('Name')),
# #                     'institute': safe_strip(cert_data.get('Institute/Issuing organization')),
# #                     'completion_date': format_date(cert_data.get('Completion date')), # Use helper
# #                     'expiration_date': format_date(cert_data.get('Expiration date')), # Use helper
# #                     'score': safe_strip(cert_data.get('Score')),
# #                     'link': format_url(cert_data.get('URL/Link')), # Use helper
# #                     'description': safe_strip(cert_data.get('Description')),
# #                 })
# #
# #     # 8. Languages
# #     wizard_data['languages'] = []
# #     raw_langs = parsed_data.get('Languages')
# #     if isinstance(raw_langs, list):
# #         for lang_data in raw_langs:
# #              if isinstance(lang_data, dict):
# #                 wizard_data['languages'].append({
# #                     'language_name': safe_strip(lang_data.get('Language name')),
# #                     'proficiency': safe_strip(lang_data.get('Proficiency'), 'basic'), # Default
# #                 })
# #
# #     # 9. Custom/Additional Sections
# #     wizard_data['custom_sections'] = []
# #     raw_custom = parsed_data.get('Additional sections') # Check for 'Additional sections' key
# #     if isinstance(raw_custom, list):
# #         for custom_data in raw_custom:
# #             if isinstance(custom_data, dict):
# #                 bullets_raw = custom_data.get('Bullet points', [])
# #                 # Format bullets as a newline-separated string for CustomData model
# #                 formatted_bullets_str = ""
# #                 if isinstance(bullets_raw, list):
# #                     formatted_bullets_str = "\n".join(f"• {safe_strip(b)}" for b in bullets_raw if isinstance(b, str) and safe_strip(b))
# #                 elif isinstance(bullets_raw, str):
# #                     lines = [safe_strip(b) for b in bullets_raw.split('\n') if safe_strip(b)]
# #                     # Add bullet prefix if not already present
# #                     formatted_bullets_str = "\n".join(f"• {line}" if not line.startswith(('•', '*', '-')) else line for line in lines)
# #
# #                 wizard_data['custom_sections'].append({
# #                     'name': safe_strip(custom_data.get('Section name')), # Map key correctly
# #                     'completion_date': format_date(custom_data.get('Completion date')), # Use helper
# #                     'bullet_points': formatted_bullets_str, # Store as string
# #                     'description': safe_strip(custom_data.get('Description')),
# #                     'link': format_url(custom_data.get('URL/Link')), # Use helper
# #                     'institution_name': safe_strip(custom_data.get('Institution name')),
# #                 })
# #
# #     print("--- Transformation complete ---")
# #     # print(json.dumps(wizard_data, indent=2)) # Optional: Print transformed data for debugging
# #     return wizard_data
# #
# # # --- Views ---
# #
# # @login_required
# # def template_selection(request):
# #     """Displays template options for the user to select."""
# #     print("==== ENTERING template_selection VIEW ====")
# #     from_upload = request.session.get('from_resume_upload', False)
# #     # Example templates - replace with your actual template data source if needed
# #     templates = [
# #         {
# #             'id': 1, 'name': 'Professional Classic',
# #             'description': 'A clean and traditional format, ATS-friendly.',
# #             'thumbnail': 'img/templates/1.jpg', # Ensure path is correct relative to static files
# #             'tags': ['Classic', 'ATS-Friendly', 'Traditional']
# #         },
# #         {
# #             'id': 2, 'name': 'Modern Minimalist',
# #             'description': 'Sleek design focusing on readability and key info.',
# #             'thumbnail': 'img/templates/2.jpg',
# #             'tags': ['Modern', 'Minimalist', 'Clean']
# #         },
# #          {
# #             'id': 3, 'name': 'Executive Style',
# #             'description': 'Elegant and formal, suitable for senior roles.',
# #             'thumbnail': 'img/templates/3.jpg',
# #             'tags': ['Executive', 'Formal', 'Senior Level']
# #         },
# #         {
# #             'id': 4, 'name': 'Technical Focus',
# #             'description': 'Highlights technical skills, projects, and certifications.',
# #             'thumbnail': 'img/templates/4.jpg',
# #             'tags': ['Technical', 'Skills-Focused', 'IT']
# #         },
# #         {
# #             'id': 5, 'name': 'Clean Professional',
# #             'description': 'A modern take on professional resumes with clear sections.',
# #             'thumbnail': 'img/templates/5.jpg',
# #             'tags': ['Professional', 'Clean', 'Modern']
# #         },
# #         {
# #             'id': 6, 'name': 'Fresh Graduate',
# #             'description': 'Emphasizes education, projects, and internships.',
# #             'thumbnail': 'img/templates/6.jpg',
# #             'tags': ['Entry-Level', 'Academic', 'Internship']
# #         },
# #         # Add more templates as needed
# #     ]
# #     is_debug = getattr(settings, 'DEBUG', False)
# #     return render(request, 'resumes/template_select.html', {
# #         'templates': templates, 'from_upload': from_upload, 'debug': is_debug
# #     })
# #
# #
# # @login_required
# # @require_http_methods(["POST"])
# # def select_template(request):
# #     """Handles template selection and initiates the wizard flow."""
# #     print("==== ENTERING select_template VIEW (Upload-to-Wizard Flow Enabled) ====")
# #     template_id = request.POST.get('template_id')
# #     if not template_id:
# #         messages.error(request, "Please select a template")
# #         return redirect('job_portal:template_selection')
# #
# #     request.session['resume_template_id'] = template_id
# #     from_upload = request.session.get('from_resume_upload', False)
# #
# #     # Clear previous wizard data if starting anew or from upload
# #     request.session['resume_form_data'] = {}
# #     request.session['resume_wizard_step'] = 1 # Reset to step 1
# #
# #     if from_upload:
# #         print("Processing uploaded resume data for wizard...")
# #         parsed_data_json = request.session.get('parsed_resume_data')
# #         if parsed_data_json:
# #             try:
# #                 parsed_data = json.loads(parsed_data_json)
# #                 # Transform data *before* putting it into 'resume_form_data'
# #                 transformed_data = transform_parsed_data_to_wizard_format(parsed_data)
# #                 request.session['resume_form_data'] = transformed_data # Store transformed data
# #                 # Clean up upload-specific session keys
# #                 if 'parsed_resume_data' in request.session: del request.session['parsed_resume_data']
# #                 if 'from_resume_upload' in request.session: del request.session['from_resume_upload']
# #                 if 'resume_ai_engine' in request.session: del request.session['resume_ai_engine']
# #                 request.session.modified = True # Ensure session is saved
# #                 messages.info(request, "Your uploaded resume data has been loaded. Please review each section.")
# #                 return redirect('job_portal:resume_wizard', step=1)
# #             except json.JSONDecodeError as json_err:
# #                  print(f"ERROR decoding parsed JSON data: {json_err}")
# #                  messages.error(request, f"Error loading parsed resume data (invalid format): {json_err}. Please try uploading again.")
# #                  return redirect('job_portal:upload_resume')
# #             except Exception as e:
# #                 print(f"ERROR transforming or processing parsed data: {e}"); traceback.print_exc()
# #                 messages.error(request, f"Error processing parsed resume data: {e}. Please try uploading again.")
# #                 # Clear potentially corrupted data
# #                 if 'parsed_resume_data' in request.session: del request.session['parsed_resume_data']
# #                 request.session['resume_form_data'] = {}
# #                 request.session.modified = True
# #                 return redirect('job_portal:upload_resume')
# #         else:
# #             messages.error(request, "Parsed resume data not found in session. Please try uploading again.")
# #             return redirect('job_portal:upload_resume')
# #     else: # Create from Scratch
# #         print("Starting wizard from scratch.")
# #         # Session data already cleared above
# #         request.session.modified = True
# #         return redirect('job_portal:resume_wizard', step=1)
# #
# #
# # # --- Wizard View (With Manual Formset Validation Loop - Corrected) ---
# # @login_required
# # def resume_wizard(request, step):
# #     """Handle the multi-step form wizard for resume creation."""
# #     print(f"\n==== ENTERING resume_wizard VIEW for step {step} ({request.method}) ====")
# #
# #     template_id = request.session.get('resume_template_id')
# #     if not template_id:
# #         messages.error(request, "Please select a template first.")
# #         return redirect('job_portal:template_selection')
# #
# #     # Load current wizard data from session
# #     form_data = request.session.get('resume_form_data', {})
# #     print(f"Session form_data loaded for step {step}: {list(form_data.keys())}")
# #
# #     # Define Formsets using formset_factory for session data compatibility
# #     # Using extra=1 to match the template's expectation for adding new forms
# #     SkillFormSet = formset_factory(SkillForm, extra=1, can_delete=True)
# #     ExperienceFormSet = formset_factory(ExperienceForm, extra=1, can_delete=True)
# #     EducationFormSet = formset_factory(EducationForm, extra=1, can_delete=True) # Keep extra=1
# #     ProjectFormSet = formset_factory(ProjectForm, extra=1, can_delete=True)
# #     CertificationFormSet = formset_factory(CertificationForm, extra=1, can_delete=True)
# #     LanguageFormSet = formset_factory(LanguageForm, extra=1, can_delete=True)
# #     CustomDataFormSet = formset_factory(CustomDataForm, extra=1, can_delete=True)
# #
# #     # Wizard step configuration
# #     steps_config = {
# #         1: {'title': 'Personal Information', 'form_class': ResumeBasicInfoForm, 'template': 'resumes/wizard_steps/personal_info.html', 'data_key': 'personal_info'},
# #         2: {'title': 'Professional Summary', 'form_class': ResumeSummaryForm, 'template': 'resumes/wizard_steps/summary.html', 'data_key': 'summary'},
# #         3: {'title': 'Skills', 'formset_class': SkillFormSet, 'template': 'resumes/wizard_steps/skills.html', 'data_key': 'skills'},
# #         4: {'title': 'Work Experience', 'formset_class': ExperienceFormSet, 'template': 'resumes/wizard_steps/experience.html', 'data_key': 'experiences'},
# #         5: {'title': 'Education', 'formset_class': EducationFormSet, 'template': 'resumes/wizard_steps/education.html', 'data_key': 'educations'},
# #         6: {'title': 'Projects', 'formset_class': ProjectFormSet, 'template': 'resumes/wizard_steps/projects.html', 'data_key': 'projects'},
# #         7: {'title': 'Certifications', 'formset_class': CertificationFormSet, 'template': 'resumes/wizard_steps/certifications.html', 'data_key': 'certifications'},
# #         8: {'title': 'Languages', 'formset_class': LanguageFormSet, 'template': 'resumes/wizard_steps/languages.html', 'data_key': 'languages'},
# #         9: {'title': 'Additional Sections', 'formset_class': CustomDataFormSet, 'template': 'resumes/wizard_steps/custom_sections.html', 'data_key': 'custom_sections'},
# #     }
# #
# #     # Validate step number
# #     try:
# #         step = int(step)
# #         if step < 1 or step > len(steps_config):
# #             print(f"Invalid step number ({step}). Redirecting to step 1.")
# #             return redirect('job_portal:resume_wizard', step=1)
# #     except ValueError:
# #         print(f"Invalid step value ('{step}'). Redirecting to step 1.")
# #         return redirect('job_portal:resume_wizard', step=1)
# #
# #     # Update current step in session
# #     request.session['resume_wizard_step'] = step
# #     step_info = steps_config[step]
# #     data_key = step_info['data_key']
# #     template_name = step_info['template']
# #     form = None       # To hold the form instance if step uses a single form
# #     formset = None    # To hold the formset instance if step uses a formset
# #
# #     # --- POST Request Handling ---
# #     if request.method == 'POST':
# #         print(f"Processing POST for step {step} ('{data_key}')")
# #         is_valid_overall = True # Assume valid initially for the whole step
# #
# #         # --- Single Form Steps (1, 2) ---
# #         if step_info.get('form_class'):
# #             form = step_info['form_class'](request.POST)
# #             if form.is_valid():
# #                 cleaned_data = form.cleaned_data.copy()
# #                 # Convert dates to strings for session serialization
# #                 for field, value in cleaned_data.items():
# #                     if isinstance(value, date):
# #                         cleaned_data[field] = value.strftime('%Y-%m-%d')
# #                 form_data[data_key] = cleaned_data # Update session data
# #                 print(f"Step {step} form is valid. Data updated.")
# #             else:
# #                 print(f"Form errors step {step}: {form.errors.as_json()}")
# #                 messages.error(request, f"Please correct the errors in the '{step_info['title']}' section.")
# #                 is_valid_overall = False
# #
# #         # --- Formset Steps (3-9) ---
# #         elif step_info.get('formset_class'):
# #             prefix = f'step{step}_{data_key}' # Unique prefix for the formset
# #             CurrentFormSet = step_info['formset_class']
# #             formset = CurrentFormSet(request.POST, prefix=prefix)
# #
# #             # --- Manual Validation Loop for Formsets ---
# #             cleaned_data_list = []
# #             any_form_errors = False # Flag to check if any form has errors
# #
# #             # Check management form validity FIRST using the correct attribute
# #             if not formset.management_form.is_valid():
# #                  print(f"Management form errors step {step}: {formset.management_form.errors}")
# #                  messages.error(request, f"There was a problem processing the {step_info['title']} section structure. Please try again.")
# #                  is_valid_overall = False
# #             else:
# #                 # Iterate through each form in the formset
# #                 for form_instance in formset.forms:
# #                     # 1. Skip forms marked for deletion (check POST directly)
# #                     delete_key = f'{form_instance.prefix}-DELETE'
# #                     if formset.can_delete and request.POST.get(delete_key):
# #                         print(f"  Skipping deleted form (POST check): {form_instance.prefix}")
# #                         continue # Move to the next form
# #
# #                     # 2. Validate this specific form IF it wasn't marked for deletion
# #                     print(f"  Checking form: {form_instance.prefix}")
# #                     if form_instance.is_valid():
# #                         # 3. Now check if it actually changed (to skip blank extra forms that passed validation)
# #                         if not form_instance.has_changed():
# #                             print(f"  Skipping unchanged valid form: {form_instance.prefix}")
# #                             continue # Move to the next form
# #
# #                         # 4. Process valid, changed, non-deleted forms
# #                         print(f"  Processing valid, changed form: {form_instance.prefix}")
# #                         form_instance_data = form_instance.cleaned_data
# #                         if not form_instance_data: continue # Safeguard
# #
# #                         entry_data = form_instance_data.copy()
# #                         entry_data.pop('DELETE', None) # Ensure DELETE is removed
# #
# #                         # Convert dates to strings
# #                         for field, value in entry_data.items():
# #                             if isinstance(value, date):
# #                                 entry_data[field] = value.strftime('%Y-%m-%d')
# #
# #                         # --- Handle Bullet Points Manually ---
# #                         if data_key in ['experiences', 'projects', 'custom_sections']:
# #                             current_bullets = []
# #                             form_prefix = form_instance.prefix
# #                             match = re.search(r'-(\d+)$', form_prefix)
# #                             if match:
# #                                 form_index = int(match.group(1))
# #                                 bullet_index = 0
# #                                 # *** USE CORRECTED NAME PATTERN ***
# #                                 bullet_name_pattern = f'bullet_{form_index}_'
# #                                 # **********************************
# #                                 print(f"    Looking for bullets with pattern: {bullet_name_pattern}*") # Debug print
# #
# #                                 while True:
# #                                     bullet_field_name = f'{bullet_name_pattern}{bullet_index}'
# #                                     bullet_value = request.POST.get(bullet_field_name)
# #
# #                                     if bullet_value is None:
# #                                         if bullet_index == 0: # Log only if first bullet isn't found
# #                                              print(f"    Bullet field '{bullet_name_pattern}0' not found for {form_prefix}. Assuming no bullets or check template naming.")
# #                                         break # Stop searching
# #
# #                                     if bullet_value.strip():
# #                                         print(f"    Found bullet '{bullet_field_name}': {bullet_value[:30]}...")
# #                                         if data_key in ['experiences', 'projects']:
# #                                             current_bullets.append({'description': bullet_value.strip()})
# #                                         elif data_key == 'custom_sections':
# #                                             bullet_line = bullet_value.strip()
# #                                             if not bullet_line.startswith(('•', '*', '-')):
# #                                                 current_bullets.append(f"• {bullet_line}")
# #                                             else:
# #                                                 current_bullets.append(bullet_line)
# #                                     else:
# #                                         print(f"    Skipping empty bullet: {bullet_field_name}")
# #                                     bullet_index += 1
# #
# #                                 # Assign collected bullets
# #                                 if data_key in ['experiences', 'projects']:
# #                                     entry_data['bullet_points'] = current_bullets
# #                                     print(f"    Collected {len(current_bullets)} bullets for {form_prefix}")
# #                                 elif data_key == 'custom_sections':
# #                                      entry_data['bullet_points'] = "\n".join(current_bullets)
# #                                      print(f"    Collected {len(current_bullets)} bullet lines for {form_prefix}")
# #                             else:
# #                                 print(f"Warning: Could not extract index from form prefix '{form_prefix}' for bullet handling.")
# #                                 entry_data['bullet_points'] = [] if data_key != 'custom_sections' else ""
# #
# #                         # Add the processed data for this form instance to the list
# #                         cleaned_data_list.append(entry_data)
# #
# #                     else: # This specific form is invalid
# #                         print(f"  Individual form {form_instance.prefix} is invalid. Errors: {form_instance.errors.as_json()}")
# #                         is_valid_overall = False # Mark the whole step as invalid
# #                         any_form_errors = True # Flag that we found errors
# #
# #
# #                 # After iterating through all forms, check for non-form errors
# #                 if formset.non_form_errors():
# #                     print(f"Non-form errors step {step}: {formset.non_form_errors()}")
# #                     messages.error(request, f"There was a problem processing the {step_info['title']} section structure (non-form errors). Please try again.")
# #                     is_valid_overall = False
# #
# #             # Display general error message if any form had issues
# #             if any_form_errors:
# #                 messages.error(request, f"Please correct the errors highlighted in the '{step_info['title']}' section.")
# #                 # is_valid_overall is already False
# #
# #             # Save data to session *only if* the entire step processing was valid
# #             if is_valid_overall:
# #                 form_data[data_key] = cleaned_data_list
# #                 print(f"Step {step} formset processing complete. Saved {len(cleaned_data_list)} valid entries to session for key '{data_key}'.")
# #             else:
# #                  print(f"Step {step} formset is invalid overall. Not updating session data for '{data_key}'.")
# #
# #
# #         # --- Navigation Logic ---
# #         if is_valid_overall:
# #             # Save the updated form_data to the session
# #             request.session['resume_form_data'] = form_data
# #             request.session.modified = True # Crucial: ensure session is saved
# #             print(f"Session data saved for step {step}.")
# #
# #             # Determine next step or completion
# #             next_step = step + 1
# #             if next_step > len(steps_config):
# #                 print(f"Finished final step {step}. Redirecting to generate resume.")
# #                 # Optionally clear wizard step tracker
# #                 # request.session.pop('resume_wizard_step', None)
# #                 return redirect('job_portal:generate_resume')
# #             else:
# #                 print(f"Redirecting to step {next_step}")
# #                 return redirect('job_portal:resume_wizard', step=next_step)
# #         else:
# #             # If not valid, fall through to GET logic below to re-render the current step with errors
# #             print(f"Step {step} validation failed. Re-rendering template.")
# #             pass # Fall through
# #
# #     # --- GET Request Handling (or Invalid POST) ---
# #     print(f"Handling GET request or re-rendering after invalid POST for step {step}")
# #     context = {
# #         'step': step,
# #         'total_steps': len(steps_config),
# #         'step_title': step_info['title'],
# #         'template_id': template_id,
# #         'previous_step': step - 1 if step > 1 else None,
# #         'next_step': step + 1 if step < len(steps_config) else None, # For navigation buttons
# #         'is_final_step': step == len(steps_config),
# #     }
# #
# #     # NEW CODE: Add skills data when on the experiences step
# #     if step == 4:  # Experience step
# #         # Get skills from session data
# #         skills_data = form_data.get('skills', [])
# #         if isinstance(skills_data, list):
# #             # Serialize skills for the template
# #             import json
# #             skills_json = json.dumps(skills_data)
# #             context['skills_data'] = skills_json
# #         else:
# #             context['skills_data'] = '[]'
# #
# #     # Initialize form or formset for rendering
# #     if step_info.get('form_class'): # Steps 1, 2
# #         # If POST failed, use the invalid form instance to show errors
# #         form_to_render = form if (request.method == 'POST' and form and not is_valid_overall) else None
# #         if not form_to_render:
# #             # Get initial data from session for GET request
# #             initial_data = form_data.get(data_key, {})
# #             # Ensure data structure is correct (e.g., summary needs {'summary': ...})
# #             if step == 2:
# #                 if isinstance(initial_data, str): initial_data = {'summary': initial_data}
# #                 elif not isinstance(initial_data, dict): initial_data = {'summary': ''}
# #             elif step == 1 and not isinstance(initial_data, dict): initial_data = {} # Ensure dict for personal info
# #
# #             form_to_render = step_info['form_class'](initial=initial_data)
# #             print(f"  Initialized form for GET with initial data keys: {list(initial_data.keys())}")
# #         else:
# #              print("  Rendering form instance from invalid POST.")
# #         context['form'] = form_to_render
# #
# #     elif step_info.get('formset_class'): # Steps 3-9
# #         # If POST failed, use the invalid formset instance to show errors
# #         formset_to_render = formset if (request.method == 'POST' and formset and not is_valid_overall) else None
# #         if not formset_to_render:
# #             # Get initial data list from session for GET request
# #             prefix = f'step{step}_{data_key}' # Prefix must match POST
# #             initial_list = form_data.get(data_key, [])
# #             if not isinstance(initial_list, list):
# #                 print(f"  Warning: Initial data for step {step} ('{data_key}') is not a list. Resetting.")
# #                 initial_list = []
# #
# #             print(f"  Initializing formset for GET. Key: '{data_key}', Prefix: '{prefix}', Initial items: {len(initial_list)}")
# #             # print(f"  Initial data sample: {initial_list[:2]}") # Print sample if list is long
# #
# #             CurrentFormSet = step_info['formset_class']
# #             formset_to_render = CurrentFormSet(initial=initial_list, prefix=prefix)
# #         else:
# #              print("  Rendering formset instance from invalid POST.")
# #         context['formset'] = formset_to_render
# #
# #         # Pass any choices needed by the specific step's template
# #         if step == 3: context['skill_types'] = dict(Skill.SKILL_TYPES)
# #         if step == 5: context['degree_types'] = dict(Education.DEGREE_TYPES)
# #         if step == 8: context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
# #         # Add context for other steps if needed
# #
# #     print(f"Rendering template: {template_name} for step {step}")
# #     return render(request, template_name, context)
# # # def resume_wizard(request, step):
# # #     """Handle the multi-step form wizard for resume creation."""
# # #     print(f"\n==== ENTERING resume_wizard VIEW for step {step} ({request.method}) ====")
# # #
# # #     template_id = request.session.get('resume_template_id')
# # #     if not template_id:
# # #         messages.error(request, "Please select a template first.")
# # #         return redirect('job_portal:template_selection')
# # #
# # #     # Load current wizard data from session
# # #     form_data = request.session.get('resume_form_data', {})
# # #     print(f"Session form_data loaded for step {step}: {list(form_data.keys())}")
# # #
# # #     # Define Formsets using formset_factory for session data compatibility
# # #     # Using extra=1 to match the template's expectation for adding new forms
# # #     SkillFormSet = formset_factory(SkillForm, extra=1, can_delete=True)
# # #     ExperienceFormSet = formset_factory(ExperienceForm, extra=1, can_delete=True)
# # #     EducationFormSet = formset_factory(EducationForm, extra=1, can_delete=True) # Keep extra=1
# # #     ProjectFormSet = formset_factory(ProjectForm, extra=1, can_delete=True)
# # #     CertificationFormSet = formset_factory(CertificationForm, extra=1, can_delete=True)
# # #     LanguageFormSet = formset_factory(LanguageForm, extra=1, can_delete=True)
# # #     CustomDataFormSet = formset_factory(CustomDataForm, extra=1, can_delete=True)
# # #
# # #     # Wizard step configuration
# # #     steps_config = {
# # #         1: {'title': 'Personal Information', 'form_class': ResumeBasicInfoForm, 'template': 'resumes/wizard_steps/personal_info.html', 'data_key': 'personal_info'},
# # #         2: {'title': 'Professional Summary', 'form_class': ResumeSummaryForm, 'template': 'resumes/wizard_steps/summary.html', 'data_key': 'summary'},
# # #         3: {'title': 'Skills', 'formset_class': SkillFormSet, 'template': 'resumes/wizard_steps/skills.html', 'data_key': 'skills'},
# # #         4: {'title': 'Work Experience', 'formset_class': ExperienceFormSet, 'template': 'resumes/wizard_steps/experience.html', 'data_key': 'experiences'},
# # #         5: {'title': 'Education', 'formset_class': EducationFormSet, 'template': 'resumes/wizard_steps/education.html', 'data_key': 'educations'},
# # #         6: {'title': 'Projects', 'formset_class': ProjectFormSet, 'template': 'resumes/wizard_steps/projects.html', 'data_key': 'projects'},
# # #         7: {'title': 'Certifications', 'formset_class': CertificationFormSet, 'template': 'resumes/wizard_steps/certifications.html', 'data_key': 'certifications'},
# # #         8: {'title': 'Languages', 'formset_class': LanguageFormSet, 'template': 'resumes/wizard_steps/languages.html', 'data_key': 'languages'},
# # #         9: {'title': 'Additional Sections', 'formset_class': CustomDataFormSet, 'template': 'resumes/wizard_steps/custom_sections.html', 'data_key': 'custom_sections'},
# # #     }
# # #
# # #     # Validate step number
# # #     try:
# # #         step = int(step)
# # #         if step < 1 or step > len(steps_config):
# # #             print(f"Invalid step number ({step}). Redirecting to step 1.")
# # #             return redirect('job_portal:resume_wizard', step=1)
# # #     except ValueError:
# # #         print(f"Invalid step value ('{step}'). Redirecting to step 1.")
# # #         return redirect('job_portal:resume_wizard', step=1)
# # #
# # #     # Update current step in session
# # #     request.session['resume_wizard_step'] = step
# # #     step_info = steps_config[step]
# # #     data_key = step_info['data_key']
# # #     template_name = step_info['template']
# # #     form = None       # To hold the form instance if step uses a single form
# # #     formset = None    # To hold the formset instance if step uses a formset
# # #
# # #     # --- POST Request Handling ---
# # #     if request.method == 'POST':
# # #         print(f"Processing POST for step {step} ('{data_key}')")
# # #         is_valid_overall = True # Assume valid initially for the whole step
# # #
# # #         # --- Single Form Steps (1, 2) ---
# # #         if step_info.get('form_class'):
# # #             form = step_info['form_class'](request.POST)
# # #             if form.is_valid():
# # #                 cleaned_data = form.cleaned_data.copy()
# # #                 # Convert dates to strings for session serialization
# # #                 for field, value in cleaned_data.items():
# # #                     if isinstance(value, date):
# # #                         cleaned_data[field] = value.strftime('%Y-%m-%d')
# # #                 form_data[data_key] = cleaned_data # Update session data
# # #                 print(f"Step {step} form is valid. Data updated.")
# # #             else:
# # #                 print(f"Form errors step {step}: {form.errors.as_json()}")
# # #                 messages.error(request, f"Please correct the errors in the '{step_info['title']}' section.")
# # #                 is_valid_overall = False
# # #
# # #         # --- Formset Steps (3-9) ---
# # #         elif step_info.get('formset_class'):
# # #             prefix = f'step{step}_{data_key}' # Unique prefix for the formset
# # #             CurrentFormSet = step_info['formset_class']
# # #             formset = CurrentFormSet(request.POST, prefix=prefix)
# # #
# # #             # --- Manual Validation Loop for Formsets ---
# # #             cleaned_data_list = []
# # #             any_form_errors = False # Flag to check if any form has errors
# # #
# # #             # Check management form validity FIRST using the correct attribute
# # #             if not formset.management_form.is_valid():
# # #                  print(f"Management form errors step {step}: {formset.management_form.errors}")
# # #                  messages.error(request, f"There was a problem processing the {step_info['title']} section structure. Please try again.")
# # #                  is_valid_overall = False
# # #             else:
# # #                 # Iterate through each form in the formset
# # #                 for form_instance in formset.forms:
# # #                     # 1. Skip forms marked for deletion (check POST directly)
# # #                     delete_key = f'{form_instance.prefix}-DELETE'
# # #                     if formset.can_delete and request.POST.get(delete_key):
# # #                         print(f"  Skipping deleted form (POST check): {form_instance.prefix}")
# # #                         continue # Move to the next form
# # #
# # #                     # 2. Validate this specific form IF it wasn't marked for deletion
# # #                     print(f"  Checking form: {form_instance.prefix}")
# # #                     if form_instance.is_valid():
# # #                         # 3. Now check if it actually changed (to skip blank extra forms that passed validation)
# # #                         if not form_instance.has_changed():
# # #                             print(f"  Skipping unchanged valid form: {form_instance.prefix}")
# # #                             continue # Move to the next form
# # #
# # #                         # 4. Process valid, changed, non-deleted forms
# # #                         print(f"  Processing valid, changed form: {form_instance.prefix}")
# # #                         form_instance_data = form_instance.cleaned_data
# # #                         if not form_instance_data: continue # Safeguard
# # #
# # #                         entry_data = form_instance_data.copy()
# # #                         entry_data.pop('DELETE', None) # Ensure DELETE is removed
# # #
# # #                         # Convert dates to strings
# # #                         for field, value in entry_data.items():
# # #                             if isinstance(value, date):
# # #                                 entry_data[field] = value.strftime('%Y-%m-%d')
# # #
# # #                         # --- Handle Bullet Points Manually ---
# # #                         if data_key in ['experiences', 'projects', 'custom_sections']:
# # #                             current_bullets = []
# # #                             form_prefix = form_instance.prefix
# # #                             match = re.search(r'-(\d+)$', form_prefix)
# # #                             if match:
# # #                                 form_index = int(match.group(1))
# # #                                 bullet_index = 0
# # #                                 # *** USE CORRECTED NAME PATTERN ***
# # #                                 bullet_name_pattern = f'bullet_{form_index}_'
# # #                                 # **********************************
# # #                                 print(f"    Looking for bullets with pattern: {bullet_name_pattern}*") # Debug print
# # #
# # #                                 while True:
# # #                                     bullet_field_name = f'{bullet_name_pattern}{bullet_index}'
# # #                                     bullet_value = request.POST.get(bullet_field_name)
# # #
# # #                                     if bullet_value is None:
# # #                                         if bullet_index == 0: # Log only if first bullet isn't found
# # #                                              print(f"    Bullet field '{bullet_name_pattern}0' not found for {form_prefix}. Assuming no bullets or check template naming.")
# # #                                         break # Stop searching
# # #
# # #                                     if bullet_value.strip():
# # #                                         print(f"    Found bullet '{bullet_field_name}': {bullet_value[:30]}...")
# # #                                         if data_key in ['experiences', 'projects']:
# # #                                             current_bullets.append({'description': bullet_value.strip()})
# # #                                         elif data_key == 'custom_sections':
# # #                                             bullet_line = bullet_value.strip()
# # #                                             if not bullet_line.startswith(('•', '*', '-')):
# # #                                                 current_bullets.append(f"• {bullet_line}")
# # #                                             else:
# # #                                                 current_bullets.append(bullet_line)
# # #                                     else:
# # #                                         print(f"    Skipping empty bullet: {bullet_field_name}")
# # #                                     bullet_index += 1
# # #
# # #                                 # Assign collected bullets
# # #                                 if data_key in ['experiences', 'projects']:
# # #                                     entry_data['bullet_points'] = current_bullets
# # #                                     print(f"    Collected {len(current_bullets)} bullets for {form_prefix}")
# # #                                 elif data_key == 'custom_sections':
# # #                                      entry_data['bullet_points'] = "\n".join(current_bullets)
# # #                                      print(f"    Collected {len(current_bullets)} bullet lines for {form_prefix}")
# # #                             else:
# # #                                 print(f"Warning: Could not extract index from form prefix '{form_prefix}' for bullet handling.")
# # #                                 entry_data['bullet_points'] = [] if data_key != 'custom_sections' else ""
# # #
# # #                         # Add the processed data for this form instance to the list
# # #                         cleaned_data_list.append(entry_data)
# # #
# # #                     else: # This specific form is invalid
# # #                         print(f"  Individual form {form_instance.prefix} is invalid. Errors: {form_instance.errors.as_json()}")
# # #                         is_valid_overall = False # Mark the whole step as invalid
# # #                         any_form_errors = True # Flag that we found errors
# # #
# # #
# # #                 # After iterating through all forms, check for non-form errors
# # #                 if formset.non_form_errors():
# # #                     print(f"Non-form errors step {step}: {formset.non_form_errors()}")
# # #                     messages.error(request, f"There was a problem processing the {step_info['title']} section structure (non-form errors). Please try again.")
# # #                     is_valid_overall = False
# # #
# # #             # Display general error message if any form had issues
# # #             if any_form_errors:
# # #                 messages.error(request, f"Please correct the errors highlighted in the '{step_info['title']}' section.")
# # #                 # is_valid_overall is already False
# # #
# # #             # Save data to session *only if* the entire step processing was valid
# # #             if is_valid_overall:
# # #                 form_data[data_key] = cleaned_data_list
# # #                 print(f"Step {step} formset processing complete. Saved {len(cleaned_data_list)} valid entries to session for key '{data_key}'.")
# # #             else:
# # #                  print(f"Step {step} formset is invalid overall. Not updating session data for '{data_key}'.")
# # #
# # #
# # #         # --- Navigation Logic ---
# # #         if is_valid_overall:
# # #             # Save the updated form_data to the session
# # #             request.session['resume_form_data'] = form_data
# # #             request.session.modified = True # Crucial: ensure session is saved
# # #             print(f"Session data saved for step {step}.")
# # #
# # #             # Determine next step or completion
# # #             next_step = step + 1
# # #             if next_step > len(steps_config):
# # #                 print(f"Finished final step {step}. Redirecting to generate resume.")
# # #                 # Optionally clear wizard step tracker
# # #                 # request.session.pop('resume_wizard_step', None)
# # #                 return redirect('job_portal:generate_resume')
# # #             else:
# # #                 print(f"Redirecting to step {next_step}")
# # #                 return redirect('job_portal:resume_wizard', step=next_step)
# # #         else:
# # #             # If not valid, fall through to GET logic below to re-render the current step with errors
# # #             print(f"Step {step} validation failed. Re-rendering template.")
# # #             pass # Fall through
# # #
# # #     # --- GET Request Handling (or Invalid POST) ---
# # #     print(f"Handling GET request or re-rendering after invalid POST for step {step}")
# # #     context = {
# # #         'step': step,
# # #         'total_steps': len(steps_config),
# # #         'step_title': step_info['title'],
# # #         'template_id': template_id,
# # #         'previous_step': step - 1 if step > 1 else None,
# # #         'next_step': step + 1 if step < len(steps_config) else None, # For navigation buttons
# # #         'is_final_step': step == len(steps_config),
# # #     }
# # #
# # #     # Initialize form or formset for rendering
# # #     if step_info.get('form_class'): # Steps 1, 2
# # #         # If POST failed, use the invalid form instance to show errors
# # #         form_to_render = form if (request.method == 'POST' and form and not is_valid_overall) else None
# # #         if not form_to_render:
# # #             # Get initial data from session for GET request
# # #             initial_data = form_data.get(data_key, {})
# # #             # Ensure data structure is correct (e.g., summary needs {'summary': ...})
# # #             if step == 2:
# # #                 if isinstance(initial_data, str): initial_data = {'summary': initial_data}
# # #                 elif not isinstance(initial_data, dict): initial_data = {'summary': ''}
# # #             elif step == 1 and not isinstance(initial_data, dict): initial_data = {} # Ensure dict for personal info
# # #
# # #             form_to_render = step_info['form_class'](initial=initial_data)
# # #             print(f"  Initialized form for GET with initial data keys: {list(initial_data.keys())}")
# # #         else:
# # #              print("  Rendering form instance from invalid POST.")
# # #         context['form'] = form_to_render
# # #
# # #     elif step_info.get('formset_class'): # Steps 3-9
# # #         # If POST failed, use the invalid formset instance to show errors
# # #         formset_to_render = formset if (request.method == 'POST' and formset and not is_valid_overall) else None
# # #         if not formset_to_render:
# # #             # Get initial data list from session for GET request
# # #             prefix = f'step{step}_{data_key}' # Prefix must match POST
# # #             initial_list = form_data.get(data_key, [])
# # #             if not isinstance(initial_list, list):
# # #                 print(f"  Warning: Initial data for step {step} ('{data_key}') is not a list. Resetting.")
# # #                 initial_list = []
# # #
# # #             print(f"  Initializing formset for GET. Key: '{data_key}', Prefix: '{prefix}', Initial items: {len(initial_list)}")
# # #             # print(f"  Initial data sample: {initial_list[:2]}") # Print sample if list is long
# # #
# # #             CurrentFormSet = step_info['formset_class']
# # #             formset_to_render = CurrentFormSet(initial=initial_list, prefix=prefix)
# # #         else:
# # #              print("  Rendering formset instance from invalid POST.")
# # #         context['formset'] = formset_to_render
# # #
# # #         # Pass any choices needed by the specific step's template
# # #         if step == 3: context['skill_types'] = dict(Skill.SKILL_TYPES)
# # #         if step == 5: context['degree_types'] = dict(Education.DEGREE_TYPES)
# # #         if step == 8: context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
# # #         # Add context for other steps if needed
# # #
# # #     print(f"Rendering template: {template_name} for step {step}")
# # #     return render(request, template_name, context)
# #
# # # # job_portal/views/template_selection_view.py
# # #
# # # import json
# # # import re
# # # import traceback
# # # from django.shortcuts import render, redirect
# # # from django.contrib.auth.decorators import login_required
# # # from django.views.decorators.http import require_http_methods
# # # from django.contrib import messages
# # # from django.utils import timezone
# # # # Import BaseFormSet, BaseModelFormSet
# # # from django.forms import modelformset_factory, formset_factory, BaseFormSet, BaseModelFormSet
# # # from django.conf import settings
# # # from datetime import date
# # #
# # # # Import necessary forms and models
# # # from ..forms.resume_creation_form import (
# # #     ResumeBasicInfoForm, ResumeSummaryForm, ExperienceForm,
# # #     EducationForm, SkillForm, ProjectForm, CertificationForm, LanguageForm, CustomDataForm,
# # # )
# # # from ..models import (
# # #     Resume,
# # #     Skill, Education, Language, Experience, Project, Certification, CustomData
# # # )
# # #
# # # # Import helper functions from resume_parser_service
# # # try:
# # #     from services.resume_parser_service import format_date, format_url, format_location, safe_strip
# # # except ImportError:
# # #     print("Warning: Could not import helper functions from services.resume_parser_service.")
# # #     def safe_strip(value, default=''): return value.strip() if isinstance(value, str) else default
# # #     def format_date(d): return d
# # #     def format_url(u): return u
# # #     def format_location(l): return l if isinstance(l, str) else ""
# # #
# # #
# # # # --- transform_parsed_data_to_wizard_format ---
# # # # (Keep this function as it was)
# # # def transform_parsed_data_to_wizard_format(parsed_data):
# # #     print("--- Transforming parsed data to wizard format ---")
# # #     wizard_data = {}
# # #     if not isinstance(parsed_data, dict):
# # #         print(f"Error: parsed_data is not a dictionary (type: {type(parsed_data)}). Returning empty.")
# # #         return {}
# # #
# # #     # 1. Personal Information
# # #     pi = parsed_data.get('Personal Information', {})
# # #     if isinstance(pi, dict):
# # #         raw_email = pi.get('Email')
# # #         cleaned_email = None
# # #         if isinstance(raw_email, str):
# # #             cleaned_email = safe_strip(raw_email.replace('mailto:', ''))
# # #         wizard_data['personal_info'] = {
# # #             'first_name': safe_strip(pi.get('First name')),
# # #             'mid_name': safe_strip(pi.get('Middle name')),
# # #             'last_name': safe_strip(pi.get('Last name')),
# # #             'email': cleaned_email,
# # #             'phone': safe_strip(pi.get('Phone number')),
# # #             'address': format_location(pi.get('Address')),
# # #             'linkedin': format_url(pi.get('LinkedIn URL')),
# # #             'github': format_url(pi.get('GitHub URL')),
# # #             'portfolio': format_url(pi.get('Portfolio URL')),
# # #         }
# # #     else: wizard_data['personal_info'] = {}
# # #
# # #     # 2. Professional Summary
# # #     summary_data = parsed_data.get('Professional Summary')
# # #     wizard_data['summary'] = {'summary': safe_strip(summary_data)} if isinstance(summary_data, str) else {'summary': ''}
# # #
# # #     # 3. Skills
# # #     wizard_data['skills'] = []
# # #     raw_skills = parsed_data.get('Skills')
# # #     if isinstance(raw_skills, list):
# # #         for skill_data in raw_skills:
# # #             if isinstance(skill_data, dict):
# # #                 wizard_data['skills'].append({
# # #                     'skill_name': safe_strip(skill_data.get('Skill name')),
# # #                     'skill_type': safe_strip(skill_data.get('Skill type')),
# # #                     'proficiency_level': skill_data.get('Estimated proficiency level', 0),
# # #                 })
# # #
# # #     # 4. Work Experience
# # #     wizard_data['experiences'] = []
# # #     raw_experience = parsed_data.get('Work Experience')
# # #     if isinstance(raw_experience, list):
# # #         for exp_data in raw_experience:
# # #             if isinstance(exp_data, dict):
# # #                 bullets_raw = exp_data.get('Bullet points', [])
# # #                 formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw if isinstance(b, str) and safe_strip(b)] if isinstance(bullets_raw, list) else ([{'description': safe_strip(b)} for b in bullets_raw.split('\n') if safe_strip(b)] if isinstance(bullets_raw, str) else [])
# # #                 wizard_data['experiences'].append({
# # #                     'job_title': safe_strip(exp_data.get('Job title')),
# # #                     'employer': safe_strip(exp_data.get('Employer/Company name')),
# # #                     'location': format_location(exp_data.get('Location')),
# # #                     'start_date': format_date(exp_data.get('Start date')),
# # #                     'end_date': format_date(exp_data.get('End date')),
# # #                     'is_current': exp_data.get('Is current job', False),
# # #                     'bullet_points': formatted_bullets,
# # #                 })
# # #
# # #     # 5. Education
# # #     wizard_data['educations'] = []
# # #     raw_education = parsed_data.get('Education')
# # #     if isinstance(raw_education, list):
# # #         for edu_data in raw_education:
# # #             if isinstance(edu_data, dict):
# # #                 gpa_val = None
# # #                 try:
# # #                     gpa_str = edu_data.get('GPA');
# # #                     if gpa_str is not None: cleaned_gpa_str = re.sub(r"[^0-9.]", "", str(gpa_str)); gpa_val = float(cleaned_gpa_str) if cleaned_gpa_str else None
# # #                 except (ValueError, TypeError): gpa_val = None
# # #                 wizard_data['educations'].append({
# # #                     'school_name': safe_strip(edu_data.get('School name')),
# # #                     'location': format_location(edu_data.get('Location')),
# # #                     'degree': safe_strip(edu_data.get('Degree')),
# # #                     'degree_type': safe_strip(edu_data.get('Degree type')),
# # #                     'field_of_study': safe_strip(edu_data.get('Field of study')),
# # #                     'graduation_date': format_date(edu_data.get('Graduation date')),
# # #                     'gpa': gpa_val,
# # #                 })
# # #
# # #     # 6. Projects
# # #     wizard_data['projects'] = []
# # #     raw_projects = parsed_data.get('Projects')
# # #     if isinstance(raw_projects, list):
# # #         for proj_data in raw_projects:
# # #             if isinstance(proj_data, dict):
# # #                 bullets_raw = proj_data.get('Bullet points', [])
# # #                 formatted_bullets = [{'description': safe_strip(b)} for b in bullets_raw if isinstance(b, str) and safe_strip(b)] if isinstance(bullets_raw, list) else ([{'description': safe_strip(b)} for b in bullets_raw.split('\n') if safe_strip(b)] if isinstance(bullets_raw, str) else [])
# # #                 wizard_data['projects'].append({
# # #                     'project_name': safe_strip(proj_data.get('Project name')),
# # #                     'summary': safe_strip(proj_data.get('Summary/description')),
# # #                     'start_date': format_date(proj_data.get('Start date')),
# # #                     'completion_date': format_date(proj_data.get('Completion date')),
# # #                     'project_link': format_url(proj_data.get('Project URL')),
# # #                     'github_link': format_url(proj_data.get('GitHub URL')),
# # #                     'bullet_points': formatted_bullets,
# # #                 })
# # #
# # #     # 7. Certifications
# # #     wizard_data['certifications'] = []
# # #     raw_certs = parsed_data.get('Certifications')
# # #     if isinstance(raw_certs, list):
# # #         for cert_data in raw_certs:
# # #             if isinstance(cert_data, dict):
# # #                 wizard_data['certifications'].append({
# # #                     'name': safe_strip(cert_data.get('Name')),
# # #                     'institute': safe_strip(cert_data.get('Institute/Issuing organization')),
# # #                     'completion_date': format_date(cert_data.get('Completion date')),
# # #                     'expiration_date': format_date(cert_data.get('Expiration date')),
# # #                     'score': safe_strip(cert_data.get('Score')),
# # #                     'link': format_url(cert_data.get('URL/Link')),
# # #                     'description': safe_strip(cert_data.get('Description')),
# # #                 })
# # #
# # #     # 8. Languages
# # #     wizard_data['languages'] = []
# # #     raw_langs = parsed_data.get('Languages')
# # #     if isinstance(raw_langs, list):
# # #         for lang_data in raw_langs:
# # #              if isinstance(lang_data, dict):
# # #                 wizard_data['languages'].append({
# # #                     'language_name': safe_strip(lang_data.get('Language name')),
# # #                     'proficiency': safe_strip(lang_data.get('Proficiency')),
# # #                 })
# # #
# # #     # 9. Custom/Additional Sections
# # #     wizard_data['custom_sections'] = []
# # #     raw_custom = parsed_data.get('Additional sections')
# # #     if isinstance(raw_custom, list):
# # #         for custom_data in raw_custom:
# # #             if isinstance(custom_data, dict):
# # #                 bullets_raw = custom_data.get('Bullet points', [])
# # #                 formatted_bullets_str = ""
# # #                 if isinstance(bullets_raw, list): formatted_bullets_str = "\n".join(f"• {safe_strip(b)}" for b in bullets_raw if isinstance(b, str) and safe_strip(b))
# # #                 elif isinstance(bullets_raw, str): lines = [safe_strip(b) for b in bullets_raw.split('\n') if safe_strip(b)]; formatted_bullets_str = "\n".join(f"• {line}" if not line.startswith(('•', '*', '-')) else line for line in lines)
# # #                 wizard_data['custom_sections'].append({
# # #                     'name': safe_strip(custom_data.get('Section name')),
# # #                     'completion_date': format_date(custom_data.get('Completion date')),
# # #                     'bullet_points': formatted_bullets_str,
# # #                     'description': safe_strip(custom_data.get('Description')),
# # #                     'link': format_url(custom_data.get('URL/Link')),
# # #                     'institution_name': safe_strip(custom_data.get('Institution name')),
# # #                 })
# # #
# # #     print("--- Transformation complete ---")
# # #     return wizard_data
# # #
# # # # --- Views ---
# # #
# # # @login_required
# # # def template_selection(request):
# # #     # (Keep this view as it was)
# # #     print("==== ENTERING template_selection VIEW ====")
# # #     from_upload = request.session.get('from_resume_upload', False)
# # #     templates = [ # Example templates
# # #         {'id': 1, 'name': 'Professional', 'thumbnail': 'img/templates/1.jpg'},
# # #         {'id': 2, 'name': 'Modern', 'thumbnail': 'img/templates/2.jpg'},
# # #         {'id': 3, 'name': 'Minimal', 'thumbnail': 'img/templates/3.jpg'},
# # #         {'id': 4, 'name': 'Academic', 'thumbnail': 'img/templates/4.jpg'},
# # #         {'id': 5, 'name': 'Technical', 'thumbnail': 'img/templates/5.jpg'},
# # #         {'id': 6, 'name': 'Graduate', 'thumbnail': 'img/templates/6.jpg'},
# # #     ]
# # #     is_debug = getattr(settings, 'DEBUG', False)
# # #     return render(request, 'resumes/template_select.html', {
# # #         'templates': templates, 'from_upload': from_upload, 'debug': is_debug
# # #     })
# # #
# # #
# # # @login_required
# # # @require_http_methods(["POST"])
# # # def select_template(request):
# # #     # (Keep this view as it was)
# # #     print("==== ENTERING select_template VIEW (Upload-to-Wizard Flow Enabled) ====")
# # #     template_id = request.POST.get('template_id')
# # #     if not template_id:
# # #         messages.error(request, "Please select a template")
# # #         return redirect('job_portal:template_selection')
# # #
# # #     request.session['resume_template_id'] = template_id
# # #     from_upload = request.session.get('from_resume_upload', False)
# # #
# # #     if from_upload:
# # #         print("Processing uploaded resume data for wizard...")
# # #         parsed_data_json = request.session.get('parsed_resume_data')
# # #         if parsed_data_json:
# # #             try:
# # #                 parsed_data = json.loads(parsed_data_json)
# # #                 transformed_data = transform_parsed_data_to_wizard_format(parsed_data)
# # #                 request.session['resume_form_data'] = transformed_data
# # #                 request.session['resume_wizard_step'] = 1
# # #                 if 'parsed_resume_data' in request.session: del request.session['parsed_resume_data']
# # #                 if 'from_resume_upload' in request.session: del request.session['from_resume_upload']
# # #                 if 'resume_ai_engine' in request.session: del request.session['resume_ai_engine']
# # #                 request.session.modified = True
# # #                 messages.info(request, "Your uploaded resume data has been loaded. Please review each section.")
# # #                 return redirect('job_portal:resume_wizard', step=1)
# # #             except Exception as e:
# # #                 print(f"ERROR transforming or processing parsed data: {e}"); import traceback; traceback.print_exc()
# # #                 messages.error(request, f"Error loading parsed resume data: {e}. Please try uploading again.")
# # #                 request.session['resume_form_data'] = {}; request.session.modified = True
# # #                 if 'parsed_resume_data' in request.session: del request.session['parsed_resume_data']
# # #                 return redirect('job_portal:upload_resume')
# # #         else:
# # #             messages.error(request, "Parsed resume data not found in session. Please try uploading again.")
# # #             return redirect('job_portal:upload_resume')
# # #     else: # Create from Scratch
# # #         print("Starting wizard from scratch.")
# # #         request.session['resume_wizard_step'] = 1
# # #         request.session['resume_form_data'] = {} # Start empty
# # #         request.session.modified = True
# # #         return redirect('job_portal:resume_wizard', step=1)
# # #
# # #
# # # # --- Wizard View (Corrected POST validation for formsets ORDER) ---
# # # @login_required
# # # def resume_wizard(request, step):
# # #     """Handle the multi-step form wizard for resume creation."""
# # #     print(f"==== ENTERING resume_wizard VIEW for step {step} ====")
# # #
# # #     template_id = request.session.get('resume_template_id')
# # #     if not template_id:
# # #         messages.error(request, "Please select a template first.")
# # #         return redirect('job_portal:template_selection')
# # #
# # #     form_data = request.session.get('resume_form_data', {})
# # #
# # #     # Define Formsets using formset_factory for steps loading from session
# # #     SkillFormSet = formset_factory(SkillForm, extra=1, can_delete=True)
# # #     ExperienceFormSet = formset_factory(ExperienceForm, extra=1, can_delete=True)
# # #     EducationFormSet = formset_factory(EducationForm, extra=1, can_delete=True)
# # #     ProjectFormSet = formset_factory(ProjectForm, extra=1, can_delete=True)
# # #     CertificationFormSet = formset_factory(CertificationForm, extra=1, can_delete=True)
# # #     LanguageFormSet = formset_factory(LanguageForm, extra=1, can_delete=True)
# # #     CustomDataFormSet = formset_factory(CustomDataForm, extra=1, can_delete=True)
# # #
# # #     steps_config = {
# # #         1: {'title': 'Personal Information', 'form_class': ResumeBasicInfoForm, 'template': 'resumes/wizard_steps/personal_info.html', 'data_key': 'personal_info'},
# # #         2: {'title': 'Professional Summary', 'form_class': ResumeSummaryForm, 'template': 'resumes/wizard_steps/summary.html', 'data_key': 'summary'},
# # #         3: {'title': 'Skills', 'formset_class': SkillFormSet, 'template': 'resumes/wizard_steps/skills.html', 'data_key': 'skills'},
# # #         4: {'title': 'Work Experience', 'formset_class': ExperienceFormSet, 'template': 'resumes/wizard_steps/experience.html', 'data_key': 'experiences'},
# # #         5: {'title': 'Education', 'formset_class': EducationFormSet, 'template': 'resumes/wizard_steps/education.html', 'data_key': 'educations'},
# # #         6: {'title': 'Projects', 'formset_class': ProjectFormSet, 'template': 'resumes/wizard_steps/projects.html', 'data_key': 'projects'},
# # #         7: {'title': 'Certifications', 'formset_class': CertificationFormSet, 'template': 'resumes/wizard_steps/certifications.html', 'data_key': 'certifications'},
# # #         8: {'title': 'Languages', 'formset_class': LanguageFormSet, 'template': 'resumes/wizard_steps/languages.html', 'data_key': 'languages'},
# # #         9: {'title': 'Additional Sections', 'formset_class': CustomDataFormSet, 'template': 'resumes/wizard_steps/custom_sections.html', 'data_key': 'custom_sections'},
# # #     }
# # #
# # #     try:
# # #         step = int(step)
# # #         if step < 1 or step > len(steps_config): return redirect('job_portal:resume_wizard', step=1)
# # #     except ValueError: return redirect('job_portal:resume_wizard', step=1)
# # #
# # #     request.session['resume_wizard_step'] = step
# # #     step_info = steps_config[step]
# # #     data_key = step_info['data_key']
# # #     template_name = step_info['template']
# # #     form = None
# # #     formset = None
# # #
# # #     # --- POST Logic ---
# # #     if request.method == 'POST':
# # #         print(f"Processing POST for step {step}")
# # #         is_valid_overall = True # Assume valid initially for the whole step
# # #
# # #         if step_info.get('form_class'): # Steps 1, 2
# # #             form = step_info['form_class'](request.POST)
# # #             if form.is_valid():
# # #                 cleaned_data = form.cleaned_data.copy()
# # #                 for field, value in cleaned_data.items():
# # #                     if isinstance(value, date): cleaned_data[field] = value.strftime('%Y-%m-%d')
# # #                 form_data[data_key] = cleaned_data
# # #             else:
# # #                 print(f"Form errors step {step}: {form.errors}")
# # #                 messages.error(request, f"Please correct the errors in the {step_info['title']} section.")
# # #                 is_valid_overall = False
# # #
# # #         elif step_info.get('formset_class'): # Steps 3-9
# # #             prefix = f'step{step}_{data_key}'
# # #             CurrentFormSet = step_info['formset_class']
# # #             formset = CurrentFormSet(request.POST, prefix=prefix)
# # #
# # #             if formset.is_valid():
# # #                  print(f"Formset for step {step} overall is valid.")
# # #                  cleaned_data_list = []
# # #
# # #                  # *** MODIFICATION START: Correct order of checks ***
# # #                  for form_instance in formset.forms:
# # #                      # 1. Check for deletion first
# # #                      if formset.can_delete and form_instance.cleaned_data.get('DELETE'):
# # #                          print(f"Skipping deleted form: {form_instance.prefix}")
# # #                          continue
# # #
# # #                      # 2. Check if form has changed (to skip blank extra forms)
# # #                      if not form_instance.has_changed():
# # #                          print(f"Skipping unchanged form: {form_instance.prefix}")
# # #                          continue
# # #
# # #                      # 3. Check individual validity (usually redundant if formset.is_valid() passed, but safe)
# # #                      #    Note: formset.is_valid() ALREADY calls this, so this check is mostly for clarity
# # #                      #    or if you have specific per-form logic after initial validation.
# # #                      #    We rely on the main formset.is_valid() check above.
# # #                      # if not form_instance.is_valid():
# # #                      #     print(f"Individual form {form_instance.prefix} is invalid after has_changed(). Errors: {form_instance.errors}")
# # #                      #     is_valid_overall = False
# # #                      #     # Optionally break or continue collecting all errors
# # #                      #     continue # Skip this invalid form
# # #
# # #                      # 4. Process valid, changed, non-deleted forms
# # #                      form_instance_data = form_instance.cleaned_data
# # #                      if not form_instance_data: continue # Skip if cleaned_data is empty for some reason
# # #
# # #                      # Check for meaningful data (optional, but can prevent saving truly empty forms)
# # #                      has_data = False
# # #                      required_fields = []
# # #                      if step == 3: required_fields = ['skill_name']
# # #                      elif step == 4: required_fields = ['job_title']
# # #                      elif step == 5: required_fields = ['school_name']
# # #                      elif step == 6: required_fields = ['project_name']
# # #                      elif step == 7: required_fields = ['name']
# # #                      elif step == 8: required_fields = ['language_name']
# # #                      elif step == 9: required_fields = ['name']
# # #                      has_data = any(form_instance_data.get(field) for field in required_fields) or \
# # #                                 any(form_instance_data.get(f) for f in form_instance.fields if f not in required_fields + ['DELETE'])
# # #
# # #                      if has_data:
# # #                          entry_data = form_instance_data.copy()
# # #                          entry_data.pop('DELETE', None) # Remove DELETE flag even if not checked
# # #
# # #                          for field, value in entry_data.items():
# # #                              if isinstance(value, date): entry_data[field] = value.strftime('%Y-%m-%d')
# # #
# # #                          # Manual Bullet Handling (Review based on template/JS)
# # #                          if data_key in ['experiences', 'projects', 'custom_sections']:
# # #                              entry_data['bullet_points'] = [] # Initialize
# # #                              form_prefix_to_check = form_instance.prefix
# # #                              form_index_str = form_prefix_to_check.split('-')[-1]
# # #                              if form_index_str.isdigit():
# # #                                  form_index = int(form_index_str)
# # #                                  bullet_key_prefix = f'bullet_{data_key}_{form_index}_'
# # #                                  bullet_index = 0
# # #                                  collected_bullets = []
# # #                                  while True:
# # #                                      bullet_field_name = f'{bullet_key_prefix}{bullet_index}'
# # #                                      bullet_value = request.POST.get(bullet_field_name)
# # #                                      if bullet_value is None: break
# # #                                      if bullet_value.strip():
# # #                                          if data_key in ['experiences', 'projects']: collected_bullets.append({'description': bullet_value.strip()})
# # #                                          elif data_key == 'custom_sections': collected_bullets.append(f"• {bullet_value.strip()}")
# # #                                      bullet_index += 1
# # #                                  if data_key in ['experiences', 'projects']: entry_data['bullet_points'] = collected_bullets
# # #                                  elif data_key == 'custom_sections': entry_data['bullet_points'] = "\n".join(collected_bullets)
# # #
# # #                          cleaned_data_list.append(entry_data)
# # #                      else:
# # #                          print(f"Skipping form {form_instance.prefix} because core fields seem empty despite has_changed()=True.")
# # #                  # *** MODIFICATION END ***
# # #
# # #                  # Only save if the overall step remained valid (no individual form errors encountered if checked)
# # #                  if is_valid_overall:
# # #                      form_data[data_key] = cleaned_data_list
# # #                      print(f"Saved {len(cleaned_data_list)} valid entries for step {step} to session.")
# # #                  # No 'else' needed here, is_valid_overall handles flow below
# # #
# # #             else: # Formset is invalid
# # #                  print(f"Formset errors step {step}: {formset.errors}")
# # #                  print(f"Non-form errors step {step}: {formset.non_form_errors()}")
# # #                  for form_instance in formset: # Log errors for each specific form
# # #                      if form_instance.errors: print(f"Errors in form {form_instance.prefix}: {form_instance.errors}")
# # #                  messages.error(request, f"Please correct the errors in the {step_info['title']} section.")
# # #                  is_valid_overall = False # Mark step as invalid
# # #
# # #         # Redirect if valid, else fall through to re-render
# # #         if is_valid_overall:
# # #             request.session['resume_form_data'] = form_data
# # #             request.session.modified = True
# # #             next_step = step + 1
# # #             if next_step > len(steps_config):
# # #                 print(f"Finished step {step}. Redirecting to generate resume.")
# # #                 return redirect('job_portal:generate_resume')
# # #             else:
# # #                 print(f"Saved step {step} data to session. Redirecting to step {next_step}")
# # #                 return redirect('job_portal:resume_wizard', step=next_step)
# # #         # else: Fall through to GET logic below
# # #
# # #     # --- GET Logic ---
# # #     context = {
# # #         'step': step, 'total_steps': len(steps_config), 'step_title': step_info['title'],
# # #         'template_id': template_id, 'previous_step': step - 1 if step > 1 else None,
# # #         'next_step': step + 1 if step < len(steps_config) else None,
# # #     }
# # #
# # #     if step_info.get('form_class'): # Steps 1, 2
# # #         form_to_render = form if (request.method == 'POST' and form and not form.is_valid()) else None
# # #         if not form_to_render:
# # #             initial_data = form_data.get(data_key, {})
# # #             if step == 2 and isinstance(initial_data, str): initial_data = {'summary': initial_data}
# # #             elif step == 2 and not isinstance(initial_data, dict): initial_data = {'summary': ''}
# # #             elif step == 1 and not isinstance(initial_data, dict): initial_data = {}
# # #             form_to_render = step_info['form_class'](initial=initial_data)
# # #         context['form'] = form_to_render
# # #
# # #     elif step_info.get('formset_class'): # Steps 3-9
# # #          prefix = f'step{step}_{data_key}'
# # #          formset_to_render = formset if (request.method == 'POST' and formset and not formset.is_valid()) else None
# # #          if not formset_to_render:
# # #              initial_list = form_data.get(data_key, [])
# # #              if not isinstance(initial_list, list):
# # #                  print(f"Warning: Initial data for step {step} ('{data_key}') is not a list (type: {type(initial_list)}). Resetting to empty list.")
# # #                  initial_list = []
# # #
# # #              # Keep debug prints active for relevant steps
# # #              if step in [3, 4, 5]:
# # #                  print(f"\n--- WIZARD DEBUG (Step {step} GET) ---")
# # #                  print(f"1. Data Key: '{data_key}'")
# # #                  print(f"2. Initial List from Session ('{data_key}'):")
# # #                  try: import json; print(json.dumps(initial_list, indent=2))
# # #                  except ImportError: print(initial_list)
# # #                  print(f"3. Type of Initial List: {type(initial_list)}")
# # #                  print(f"4. Number of items in Initial List: {len(initial_list)}")
# # #
# # #              CurrentFormSet = step_info['formset_class']
# # #              formset_to_render = CurrentFormSet(initial=initial_list, prefix=prefix)
# # #
# # #              # Keep debug prints active for relevant steps
# # #              if step in [3, 4, 5]:
# # #                  print(f"5. Formset Object Created: {formset_to_render}")
# # #                  try:
# # #                      actual_form_count = len(formset_to_render.forms)
# # #                      initial_count = len(formset_to_render.initial_forms)
# # #                      print(f"6. Formset Initial Form Count: {initial_count}")
# # #                      print(f"7. Formset Total Form Count: {formset_to_render.total_form_count()}")
# # #                      print(f"8. Number of forms in formset.forms: {actual_form_count}")
# # #                      if actual_form_count > 0:
# # #                          first_form_initial = getattr(formset_to_render.forms[0], 'initial', 'N/A')
# # #                          print(f"9. First form's initial data (bound): {first_form_initial}")
# # #                          first_form_errors = getattr(formset_to_render.forms[0], 'errors', 'N/A')
# # #                          print(f"10. First form's errors: {first_form_errors}")
# # #                      non_form_errors = getattr(formset_to_render, 'non_form_errors', lambda: 'N/A')()
# # #                      print(f"11. Formset non_form_errors: {non_form_errors}")
# # #                  except Exception as e_debug:
# # #                      print(f"Error accessing formset properties for debugging: {e_debug}")
# # #                  print(f"--- END WIZARD DEBUG (Step {step}) ---")
# # #
# # #          context['formset'] = formset_to_render
# # #          # Pass choices needed by templates
# # #          if step == 3: context['skill_types'] = dict(Skill.SKILL_TYPES)
# # #          if step == 5: context['degree_types'] = dict(Education.DEGREE_TYPES)
# # #          if step == 8: context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
# # #          if step == 9: context['default_ideas'] = [ {"name": "Volunteer", "icon": "..."}, {"name": "Awards", "icon": "..."} ]
# # #
# # #     print(f"Rendering template: {template_name} for step {step} (GET or Invalid POST)")
# # #     return render(request, template_name, context)