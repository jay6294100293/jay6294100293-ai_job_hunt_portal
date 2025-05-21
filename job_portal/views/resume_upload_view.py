# job_portal/views/resume_upload_view.py

import os
import traceback
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db import transaction

# Service and Form imports
from services.parser.resume_parser_service import ResumeParserService
from ..forms.resume_upload_form import ResumeUploadForm

# Model imports
from ..models import (
    Resume, Skill, Experience, Education, Certification, Project, Language, CustomData,
    ExperienceBulletPoint, ProjectBulletPoint
)


@login_required
def upload_resume(request):
    """
    Handles resume file uploads. Parses the file, creates a new DRAFT resume,
    populates it with parsed data, and redirects to the editing wizard.
    """
    form = ResumeUploadForm(request.POST or None, request.FILES or None)
    template_name = 'resumes/upload_resume.html'

    if request.method == 'POST':
        if form.is_valid():
            resume_file = request.FILES['resume_file']
            ai_choice = form.cleaned_data.get('ai_engine', 'gemini')
            ai_parsing_enabled = form.cleaned_data.get('ai_parsing_enabled', True)

            # Define temporary storage location for uploaded resumes
            temp_storage_location = os.path.join(settings.MEDIA_ROOT, 'temp_resumes')
            if not os.path.exists(temp_storage_location):
                os.makedirs(temp_storage_location, exist_ok=True)

            fs = FileSystemStorage(location=temp_storage_location)
            saved_filename = fs.save(resume_file.name, resume_file)
            file_path = fs.path(saved_filename)

            parser_service = ResumeParserService(
                user_openai_key=request.user.openai_api_key if hasattr(request.user, 'openai_api_key') else None,
                user_gemini_key=request.user.gemini_api_key if hasattr(request.user, 'gemini_api_key') else None
            )

            file_extension = os.path.splitext(saved_filename)[1].lower().strip('.')
            parsed_result = parser_service.parse_resume(
                file_path=file_path,
                file_type=file_extension,
                ai_parsing_enabled=ai_parsing_enabled,
                ai_provider=ai_choice
            )

            # Prepare for redirection
            target_url_name_on_error = 'upload_resume'
            new_resume_id_for_success_redirect = None

            if "error" in parsed_result:
                messages.error(request, parsed_result["error"])
            else:
                # Create a new draft resume
                new_resume_title = f"Draft from {resume_file.name}"
                max_title_length = Resume._meta.get_field('title').max_length
                if len(new_resume_title) > max_title_length:
                    new_resume_title = new_resume_title[:max_title_length - 3] + "..."

                try:
                    with transaction.atomic():
                        new_resume = Resume.objects.create(
                            user=request.user,
                            title=new_resume_title,
                            publication_status=Resume.DRAFT,
                            status='uploaded',  # Mark as uploaded
                            source_uploaded_file=resume_file
                        )

                        # Process the parsed data
                        _populate_resume_from_parsed_data(new_resume, parsed_result)

                    messages.success(request,
                                     f"Draft resume '{new_resume.title}' created and populated. You can now review and edit it.")
                    new_resume_id_for_success_redirect = new_resume.id

                except Exception as e:
                    messages.error(request,
                                   f"An error occurred while saving the resume to the database: {str(e)}. {traceback.format_exc()}")
                    target_url_name_on_error = 'resume_creation_choice'

            # Cleanup the temporary file
            if fs.exists(saved_filename):
                try:
                    fs.delete(saved_filename)
                except OSError as e:
                    messages.warning(request, f"Could not remove temporary file '{saved_filename}': {e}")

            if new_resume_id_for_success_redirect:
                return redirect('job_portal:edit_resume_section',
                                resume_id=new_resume_id_for_success_redirect,
                                section_slug='personal-info')
            else:
                # If an error occurred (parsing or DB), re-render the upload form or redirect to choice
                current_form_instance = form if form.is_bound else ResumeUploadForm()
                return render(request, template_name, {'form': current_form_instance})

        else:  # Form is not valid
            messages.error(request, "There was an error with your submission. Please check the file and options.")
            return render(request, template_name, {'form': form})  # Re-render with form errors

    # For GET request
    return render(request, template_name, {'form': form})


def _populate_resume_from_parsed_data(resume_instance, parsed_data_dict):
    """
    Helper to populate a Resume instance and its related objects from parsed data.
    """
    with transaction.atomic():
        # Personal Info (direct fields on Resume)
        p_info = parsed_data_dict.get('personal_info', {})
        for field, value in p_info.items():
            if hasattr(resume_instance, field) and value is not None:
                setattr(resume_instance, field, value)

        # Summary (direct field on Resume)
        summary_text = parsed_data_dict.get('summary', {}).get('summary_text', '')
        if not summary_text and isinstance(parsed_data_dict.get('summary'), str):
            summary_text = parsed_data_dict.get('summary')

        if summary_text:
            resume_instance.summary = summary_text
        resume_instance.save()

        # Helper to populate related items
        def populate_related(model_class, data_key, foreign_key_field='resume'):
            related_manager = getattr(resume_instance, model_class._meta.get_field(foreign_key_field).related_name)
            items_data = parsed_data_dict.get(data_key, [])
            for item_data in items_data:
                if not item_data: continue

                # Handle bullet points for Experience and Project
                bullets_data = None
                if data_key == 'experiences' and 'bullet_points' in item_data:
                    bullets_data = item_data.pop('bullet_points', [])
                elif data_key == 'projects' and 'bullet_points' in item_data:
                    bullets_data = item_data.pop('bullet_points', [])

                # Update field names if they don't match the model
                if data_key == 'educations' or data_key == 'education':
                    if 'degree' in item_data and 'degree_name' not in item_data:
                        item_data['degree_name'] = item_data.pop('degree')

                if data_key == 'certifications':
                    if 'institute' in item_data and 'issuing_organization' not in item_data:
                        item_data['issuing_organization'] = item_data.pop('institute')
                    if 'completion_date' in item_data and 'issue_date' not in item_data:
                        item_data['issue_date'] = item_data.pop('completion_date')

                if data_key == 'projects':
                    if 'project_name' not in item_data and 'name' in item_data:
                        item_data['project_name'] = item_data.pop('name')

                # Filter out keys not in model
                valid_fields = {f.name for f in model_class._meta.get_fields()}
                filtered_item_data = {k: v for k, v in item_data.items() if k in valid_fields}

                if filtered_item_data:  # Ensure there's something to save
                    obj = model_class.objects.create(**{foreign_key_field: resume_instance}, **filtered_item_data)

                    # Process bullet points
                    if bullets_data and data_key in ['experiences', 'experience']:
                        for bullet in bullets_data:
                            if isinstance(bullet, dict) and 'description' in bullet:
                                ExperienceBulletPoint.objects.create(experience=obj, description=bullet['description'])
                            elif isinstance(bullet, str):
                                ExperienceBulletPoint.objects.create(experience=obj, description=bullet)

                    elif bullets_data and data_key in ['projects', 'project']:
                        for bullet in bullets_data:
                            if isinstance(bullet, dict) and 'description' in bullet:
                                ProjectBulletPoint.objects.create(project=obj, description=bullet['description'])
                            elif isinstance(bullet, str):
                                ProjectBulletPoint.objects.create(project=obj, description=bullet)

        # Populate all related sections
        populate_related(Experience, 'experiences')
        populate_related(Experience, 'experience')  # Handle alternate key name
        populate_related(Education, 'educations')
        populate_related(Education, 'education')  # Handle alternate key name
        populate_related(Skill, 'skills')
        populate_related(Project, 'projects')
        populate_related(Project, 'project')  # Handle alternate key name
        populate_related(Certification, 'certifications')
        populate_related(Certification, 'certification')  # Handle alternate key name
        populate_related(Language, 'languages')
        populate_related(Language, 'language')  # Handle alternate key name
        populate_related(CustomData, 'custom_sections')
        populate_related(CustomData, 'custom_data')  # Handle alternate key name

# Ensure any obsolete views like preview_upload_data or create_resume_from_upload
# that might have been in this file originally are removed.

# # job_portal/views/resume_upload_view.py
#
# import time
# import json
# import traceback # Import traceback for detailed error logging
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# # from django.core.files.storage import FileSystemStorage # Likely not needed now
# from django.conf import settings
# from django.views.decorators.http import require_http_methods # Keep if used elsewhere
#
# from .resume_save_section_view import save_section
#
# from ..forms.resume_upload_form import ResumeUploadForm
# from ..models import Resume, APIUsage # Keep other models if used in other functions in this file
#
#
#
#
#
# @login_required
# def upload_resume(request):
#     """
#     Handle the upload of an existing resume document and process it with AI.
#     """
#     print("==== ENTERING upload_resume VIEW ====")
#     print(f"Request method: {request.method}")
#
#     if request.method == 'POST':
#         print("Processing POST request")
#         form = ResumeUploadForm(request.POST, request.FILES)
#         print(f"Form is valid: {form.is_valid()}")
#
#         if form.is_valid():
#             # Get the AI engine choice
#             ai_engine = form.cleaned_data.get('ai_engine', 'chatgpt')
#             print(f"Selected AI engine: {ai_engine}")
#
#             # Get the uploaded file
#             resume_file = request.FILES['resume_file']
#             print(f"Uploaded file: {resume_file.name}, size: {resume_file.size} bytes")
#
#             # Check file size again server-side (using setting)
#             max_size = getattr(settings, 'RESUME_FILE_MAX_SIZE', 5 * 1024 * 1024) # Default 5MB
#             if resume_file.size > max_size:
#                  messages.error(request, f"File size exceeds the limit of {max_size // (1024*1024)}MB.")
#                  return render(request, 'resumes/upload_resume.html', {'form': form})
#
#             try:
#                 # Start timing for API response
#                 start_time = time.time()
#
#                 # --- FIX: Capture both return values ---
#                 print("Extracting text and links from resume file...")
#                 resume_text, extracted_links = extract_text_from_resume(resume_file)
#
#                 print(f"Extracted text length: {len(resume_text)} characters")
#                 print(f"Extracted links: {extracted_links}")
#
#                 # Add check for minimal text length after extraction
#                 # Using 50 as threshold (consistent with parser service)
#                 if len(resume_text) < 50:
#                     print("ERROR: Extracted text is too short. Possible extraction failure.")
#                     messages.error(request, "Could not extract sufficient text from the uploaded file. Please ensure the file is not empty or corrupted, and try a different file or format if the issue persists.")
#                     return render(request, 'resumes/upload_resume.html', {'form': form})
#
#                 # Parse resume text with AI, passing extracted links
#                 print(f"Parsing resume with {ai_engine}...")
#                 # --- FIX: Pass extracted_links ---
#                 parsed_data = parse_resume_with_ai(resume_text, extracted_links, ai_engine)
#
#                 # Calculate API response time
#                 response_time = time.time() - start_time
#                 print(f"API response time: {response_time:.2f} seconds")
#
#                 # --- FIX: Add validation after parsing ---
#                 if parsed_data is None:
#                     print("ERROR: AI parsing returned None. Upload failed.")
#                     messages.error(request, "Failed to parse resume data. The AI model might be unavailable or encountered an error. Please try again later or use the basic parser.")
#                     return render(request, 'resumes/upload_resume.html', {'form': form})
#
#                 if not isinstance(parsed_data, dict):
#                     print(f"ERROR: Parsed data is not a dictionary (type: {type(parsed_data)}). Upload failed.")
#                     messages.error(request, "Failed to process resume data due to an unexpected format received from the AI. Please try again or check the file.")
#                     return render(request, 'resumes/upload_resume.html', {'form': form})
#
#                 # Ensure required 'Personal Information' exists and is a dictionary
#                 if 'Personal Information' not in parsed_data or not isinstance(parsed_data.get('Personal Information'), dict):
#                     print("ERROR: 'Personal Information' section missing or invalid in parsed data.")
#                     messages.error(request, "Could not find essential personal information (like name, email, phone) in the resume. Please ensure these details are clearly present in your file.")
#                     # Optionally, attempt fallback or just return error
#                     return render(request, 'resumes/upload_resume.html', {'form': form})
#
#                 # Store parsed data in session for later use
#                 print("Storing parsed data in session...")
#                 try:
#                     # Attempt to serialize the data to JSON for session storage
#                     request.session['parsed_resume_data'] = json.dumps(parsed_data)
#                 except TypeError as json_err:
#                     print(f"ERROR: Could not serialize parsed_data to JSON: {json_err}")
#                     # Log the structure for debugging
#                     print(f"Problematic data structure causing serialization error: {parsed_data}")
#                     messages.error(request, f"Could not store the extracted resume data due to an internal error ({json_err}). Please try uploading again.")
#                     return render(request, 'resumes/upload_resume.html', {'form': form})
#
#                 request.session['resume_ai_engine'] = ai_engine
#                 request.session['from_resume_upload'] = True  # Flag to indicate this is from upload
#
#                 print("Session variables set:")
#                 print(f"- resume_ai_engine: {request.session.get('resume_ai_engine')}")
#                 print(f"- from_resume_upload: {request.session.get('from_resume_upload')}")
#                 print(f"- parsed_resume_data length: {len(request.session.get('parsed_resume_data', ''))}")
#
#                 # Log AI usage
#                 try:
#                     # Estimate token usage (very rough estimate)
#                     input_tokens = len(resume_text) // 4  # ~4 chars per token
#                     # Use the actual JSON string length stored in session for output estimate
#                     output_tokens = len(request.session.get('parsed_resume_data', '')) // 4
#
#                     usage = APIUsage(
#                         user=request.user,
#                         api_name=ai_engine,
#                         operation='resume_parsing',
#                         input_tokens=input_tokens,
#                         output_tokens=output_tokens,
#                         response_time=response_time,
#                         status='success'
#                         # JobInput is not linked here, maybe link later if needed
#                     )
#                     usage.calculate_cost() # This also saves
#                     print("API usage logged successfully")
#                 except Exception as e:
#                     print(f"Error logging API usage: {str(e)}")
#
#                 # Success message and redirect
#                 print("Adding success message and redirecting to template_selection")
#                 messages.success(request, "Resume uploaded and processed! Now select a template.")
#                 redirect_url = 'job_portal:template_selection'
#                 print(f"Redirecting to: {redirect_url}")
#                 return redirect(redirect_url)
#
#             # Catch specific exceptions if possible, otherwise generic Exception
#             except json.JSONDecodeError as json_err: # Catch JSON errors specifically
#                  print(f"ERROR during JSON processing: {str(json_err)}")
#                  messages.error(request, "There was an issue processing the data extracted from your resume. Please ensure the file content is standard.")
#                  traceback.print_exc()
#                  return render(request, 'resumes/upload_resume.html', {'form': form})
#             except Exception as e:
#                 print(f"ERROR during processing: {str(e)}")
#                 # Provide a more user-friendly error message
#                 messages.error(request, f"An unexpected error occurred while processing your resume: {str(e)}. Please check the file or try again.")
#                 # Log the full traceback for server-side debugging
#                 traceback.print_exc()
#                 return render(request, 'resumes/upload_resume.html', {'form': form})
#         else:
#              # Form is invalid, re-render with errors
#              print("Form validation failed.")
#              print(form.errors) # Log form errors to console
#              # Don't necessarily need a message here, form errors should display
#              # messages.error(request, "Please correct the errors below.")
#
#     else: # GET Request
#         print("Processing GET request - displaying empty form")
#         form = ResumeUploadForm()
#
#     print("Rendering upload_resume.html template")
#     return render(request, 'resumes/upload_resume.html', {'form': form})
#
#
# @login_required
# def edit_resume_section(request, resume_id, section):
#     """
#     Allow editing a specific section of the resume by loading data into the wizard.
#     """
#     print(f"==== ENTERING edit_resume_section VIEW ==== Resume ID: {resume_id}, Section: {section}")
#     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
#
#     # Prepare form data based on the selected section
#     form_data = {}
#     step = None # Initialize step
#
#     try:
#         if section == 'personal':
#             form_data['personal_info'] = {
#                 'first_name': resume.first_name, 'mid_name': resume.mid_name, 'last_name': resume.last_name,
#                 'email': resume.email, 'phone': resume.phone, 'address': resume.address,
#                 'linkedin': resume.linkedin, 'github': resume.github, 'portfolio': resume.portfolio,
#             }
#             step = 1
#         elif section == 'summary':
#             form_data['summary'] = resume.summary # Store as string directly
#             step = 2
#         elif section == 'skills':
#             form_data['skills'] = [{'skill_name': s.skill_name, 'skill_type': s.skill_type, 'proficiency_level': s.proficiency_level} for s in resume.skills.all()]
#             step = 3
#         elif section == 'experience':
#             form_data['experiences'] = []
#             for exp in resume.experiences.all().prefetch_related('bullet_points'):
#                 form_data['experiences'].append({
#                     'job_title': exp.job_title, 'employer': exp.employer, 'location': exp.location,
#                     'start_date': exp.start_date.strftime('%Y-%m-%d') if exp.start_date else None,
#                     'end_date': exp.end_date.strftime('%Y-%m-%d') if exp.end_date else None,
#                     'is_current': exp.is_current,
#                     'bullet_points': [{'description': bp.description} for bp in exp.bullet_points.all()],
#                 })
#             step = 4
#         elif section == 'education':
#             form_data['educations'] = [{
#                 'school_name': edu.school_name, 'location': edu.location, 'degree': edu.degree,
#                 'degree_type': edu.degree_type, 'field_of_study': edu.field_of_study,
#                 'graduation_date': edu.graduation_date.strftime('%Y-%m-%d') if edu.graduation_date else None,
#                 'gpa': edu.gpa,
#             } for edu in resume.educations.all()]
#             step = 5
#         elif section == 'projects':
#              form_data['projects'] = []
#              for proj in resume.projects.all().prefetch_related('bullet_points'):
#                  form_data['projects'].append({
#                      'project_name': proj.project_name, 'summary': proj.summary,
#                      'start_date': proj.start_date.strftime('%Y-%m-%d') if proj.start_date else None,
#                      'completion_date': proj.completion_date.strftime('%Y-%m-%d') if proj.completion_date else None,
#                      'project_link': proj.project_link, 'github_link': proj.github_link,
#                      'bullet_points': [{'description': bp.description} for bp in proj.bullet_points.all()],
#                  })
#              step = 6
#         elif section == 'certifications':
#              form_data['certifications'] = [{
#                  'name': cert.name, 'institute': cert.institute,
#                  'completion_date': cert.completion_date.strftime('%Y-%m-%d') if cert.completion_date else None,
#                  'expiration_date': cert.expiration_date.strftime('%Y-%m-%d') if cert.expiration_date else None,
#                  'score': cert.score, 'link': cert.link, 'description': cert.description,
#              } for cert in resume.certifications.all()]
#              step = 7
#         elif section == 'languages':
#             form_data['languages'] = [{'language_name': lang.language_name, 'proficiency': lang.proficiency} for lang in resume.languages.all()]
#             step = 8
#         elif section == 'custom':
#              form_data['custom_sections'] = [{
#                  'name': cust.name, 'completion_date': cust.completion_date.strftime('%Y-%m-%d') if cust.completion_date else None,
#                  'bullet_points': cust.bullet_points, 'description': cust.description,
#                  'link': cust.link, 'institution_name': cust.institution_name,
#              } for cust in resume.custom_data.all()]
#              step = 9
#         else:
#             print(f"ERROR: Unknown section requested for edit: {section}")
#             messages.error(request, f"Invalid section '{section}' requested for editing.")
#             return redirect('job_portal:view_resume', resume_id=resume.id)
#
#         # Store data in session for the wizard
#         print(f"Storing form data in session for editing section {section} (Step {step})")
#         # Ensure dates are strings before storing in session if they aren't already
#         # (The list comprehensions above should handle this with strftime)
#         request.session['resume_form_data'] = form_data
#         request.session['edit_resume_id'] = resume_id # Keep track of which resume is being edited
#         request.session['resume_template_id'] = request.GET.get('template', '1') # Store template ID if needed
#
#         # Clear upload flags if set
#         if 'from_resume_upload' in request.session:
#             del request.session['from_resume_upload']
#         if 'parsed_resume_data' in request.session:
#              del request.session['parsed_resume_data']
#
#         # Redirect to the appropriate step in the wizard
#         print(f"Redirecting to resume_wizard with step={step}")
#         request.session['resume_wizard_step'] = step # Set the current step
#         return redirect('job_portal:resume_wizard', step=step)
#
#     except Exception as e:
#          print(f"ERROR preparing edit section '{section}' for resume {resume_id}: {e}")
#          traceback.print_exc()
#          messages.error(request, f"An error occurred while preparing to edit the {section} section.")
#          return redirect('job_portal:view_resume', resume_id=resume.id)
#
#
# @login_required
# @require_http_methods(["POST"])
# def save_resume_section(request, resume_id):
#     """
#     Save a specific section of an edited resume.
#     Note: This might be obsolete if editing redirects to the main wizard save flow.
#     If kept, ensure it aligns with the wizard's data saving logic.
#     """
#     print(f"==== ENTERING save_resume_section VIEW ==== Resume ID: {resume_id} (Might be obsolete)")
#     # Consider if this view is still needed or if edits should go through the wizard's final save
#     return save_section(request, resume_id) # Delegate to the supporting code function
#
#
# @login_required
# def preview_upload_data(request):
#     """
#     Preview the data extracted from the uploaded resume.
#     This view is likely temporary for debugging and might be removed later.
#     """
#     print("==== ENTERING preview_upload_data VIEW ====")
#     parsed_data_json = request.session.get('parsed_resume_data')
#
#     if not parsed_data_json:
#         print("ERROR: No parsed_resume_data in session")
#         messages.error(request, "No resume data found in session. Please upload again.")
#         # Redirect to upload page instead of showing partial HTML
#         return redirect('job_portal:upload_resume')
#
#     try:
#         print("Parsing JSON data from session for preview")
#         parsed_data = json.loads(parsed_data_json)
#         print(f"Rendering preview with {len(parsed_data.keys())} data sections")
#         # Pass the template ID to the preview if available
#         template_id = request.session.get('resume_template_id', 1)
#         return render(request, 'resumes/preview_upload_data.html', {
#             'parsed_data': parsed_data,
#             'template_id': template_id # Pass template ID
#         })
#
#     except json.JSONDecodeError as json_err:
#         print(f"ERROR decoding JSON for preview: {str(json_err)}")
#         messages.error(request, "Error decoding preview data. The extracted data might be corrupted.")
#         return redirect('job_portal:upload_resume')
#     except Exception as e:
#         print(f"ERROR during preview generation: {str(e)}")
#         messages.error(request, f"An error occurred while generating the preview: {str(e)}")
#         return redirect('job_portal:upload_resume')
