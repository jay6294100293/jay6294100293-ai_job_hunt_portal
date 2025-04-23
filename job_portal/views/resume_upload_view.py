# job_portal/views/resume_upload_view.py

import os
import tempfile
import time
import json
import traceback # Import traceback for detailed error logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse # Keep JsonResponse if used elsewhere
# from django.core.files.storage import FileSystemStorage # Likely not needed now
from django.conf import settings
from django.db import transaction # Keep if used elsewhere
from django.views.decorators.http import require_http_methods # Keep if used elsewhere

# Ensure correct import path
from services.resume_parser_service import extract_text_from_resume, parse_resume_with_ai, basic_resume_parsing
from services.supporting_codes.resume_support_code import save_section # Keep if used

from ..forms.resume_upload_form import ResumeUploadForm
from ..models import Resume, APIUsage # Keep other models if used in other functions in this file


@login_required
def resume_creation_choice(request):
    """
    Display a page for users to choose between creating a new resume or uploading an existing one.
    """
    print("==== ENTERING resume_creation_choice VIEW ====")
    return render(request, 'resumes/resume_creation_choice.html')


@login_required
def upload_resume(request):
    """
    Handle the upload of an existing resume document and process it with AI.
    """
    print("==== ENTERING upload_resume VIEW ====")
    print(f"Request method: {request.method}")

    if request.method == 'POST':
        print("Processing POST request")
        form = ResumeUploadForm(request.POST, request.FILES)
        print(f"Form is valid: {form.is_valid()}")

        if form.is_valid():
            # Get the AI engine choice
            ai_engine = form.cleaned_data.get('ai_engine', 'chatgpt')
            print(f"Selected AI engine: {ai_engine}")

            # Get the uploaded file
            resume_file = request.FILES['resume_file']
            print(f"Uploaded file: {resume_file.name}, size: {resume_file.size} bytes")

            # Check file size again server-side (using setting)
            max_size = getattr(settings, 'RESUME_FILE_MAX_SIZE', 5 * 1024 * 1024) # Default 5MB
            if resume_file.size > max_size:
                 messages.error(request, f"File size exceeds the limit of {max_size // (1024*1024)}MB.")
                 return render(request, 'resumes/upload_resume.html', {'form': form})

            try:
                # Start timing for API response
                start_time = time.time()

                # --- FIX: Capture both return values ---
                print("Extracting text and links from resume file...")
                resume_text, extracted_links = extract_text_from_resume(resume_file)

                print(f"Extracted text length: {len(resume_text)} characters")
                print(f"Extracted links: {extracted_links}")

                # Add check for minimal text length after extraction
                # Using 50 as threshold (consistent with parser service)
                if len(resume_text) < 50:
                    print("ERROR: Extracted text is too short. Possible extraction failure.")
                    messages.error(request, "Could not extract sufficient text from the uploaded file. Please ensure the file is not empty or corrupted, and try a different file or format if the issue persists.")
                    return render(request, 'resumes/upload_resume.html', {'form': form})

                # Parse resume text with AI, passing extracted links
                print(f"Parsing resume with {ai_engine}...")
                # --- FIX: Pass extracted_links ---
                parsed_data = parse_resume_with_ai(resume_text, extracted_links, ai_engine)

                # Calculate API response time
                response_time = time.time() - start_time
                print(f"API response time: {response_time:.2f} seconds")

                # --- FIX: Add validation after parsing ---
                if parsed_data is None:
                    print("ERROR: AI parsing returned None. Upload failed.")
                    messages.error(request, "Failed to parse resume data. The AI model might be unavailable or encountered an error. Please try again later or use the basic parser.")
                    return render(request, 'resumes/upload_resume.html', {'form': form})

                if not isinstance(parsed_data, dict):
                    print(f"ERROR: Parsed data is not a dictionary (type: {type(parsed_data)}). Upload failed.")
                    messages.error(request, "Failed to process resume data due to an unexpected format received from the AI. Please try again or check the file.")
                    return render(request, 'resumes/upload_resume.html', {'form': form})

                # Ensure required 'Personal Information' exists and is a dictionary
                if 'Personal Information' not in parsed_data or not isinstance(parsed_data.get('Personal Information'), dict):
                    print("ERROR: 'Personal Information' section missing or invalid in parsed data.")
                    messages.error(request, "Could not find essential personal information (like name, email, phone) in the resume. Please ensure these details are clearly present in your file.")
                    # Optionally, attempt fallback or just return error
                    return render(request, 'resumes/upload_resume.html', {'form': form})

                # Store parsed data in session for later use
                print("Storing parsed data in session...")
                try:
                    # Attempt to serialize the data to JSON for session storage
                    request.session['parsed_resume_data'] = json.dumps(parsed_data)
                except TypeError as json_err:
                    print(f"ERROR: Could not serialize parsed_data to JSON: {json_err}")
                    # Log the structure for debugging
                    print(f"Problematic data structure causing serialization error: {parsed_data}")
                    messages.error(request, f"Could not store the extracted resume data due to an internal error ({json_err}). Please try uploading again.")
                    return render(request, 'resumes/upload_resume.html', {'form': form})

                request.session['resume_ai_engine'] = ai_engine
                request.session['from_resume_upload'] = True  # Flag to indicate this is from upload

                print("Session variables set:")
                print(f"- resume_ai_engine: {request.session.get('resume_ai_engine')}")
                print(f"- from_resume_upload: {request.session.get('from_resume_upload')}")
                print(f"- parsed_resume_data length: {len(request.session.get('parsed_resume_data', ''))}")

                # Log AI usage
                try:
                    # Estimate token usage (very rough estimate)
                    input_tokens = len(resume_text) // 4  # ~4 chars per token
                    # Use the actual JSON string length stored in session for output estimate
                    output_tokens = len(request.session.get('parsed_resume_data', '')) // 4

                    usage = APIUsage(
                        user=request.user,
                        api_name=ai_engine,
                        operation='resume_parsing',
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        response_time=response_time,
                        status='success'
                        # JobInput is not linked here, maybe link later if needed
                    )
                    usage.calculate_cost() # This also saves
                    print("API usage logged successfully")
                except Exception as e:
                    print(f"Error logging API usage: {str(e)}")

                # Success message and redirect
                print("Adding success message and redirecting to template_selection")
                messages.success(request, "Resume uploaded and processed! Now select a template.")
                redirect_url = 'job_portal:template_selection'
                print(f"Redirecting to: {redirect_url}")
                return redirect(redirect_url)

            # Catch specific exceptions if possible, otherwise generic Exception
            except json.JSONDecodeError as json_err: # Catch JSON errors specifically
                 print(f"ERROR during JSON processing: {str(json_err)}")
                 messages.error(request, "There was an issue processing the data extracted from your resume. Please ensure the file content is standard.")
                 traceback.print_exc()
                 return render(request, 'resumes/upload_resume.html', {'form': form})
            except Exception as e:
                print(f"ERROR during processing: {str(e)}")
                # Provide a more user-friendly error message
                messages.error(request, f"An unexpected error occurred while processing your resume: {str(e)}. Please check the file or try again.")
                # Log the full traceback for server-side debugging
                traceback.print_exc()
                return render(request, 'resumes/upload_resume.html', {'form': form})
        else:
             # Form is invalid, re-render with errors
             print("Form validation failed.")
             print(form.errors) # Log form errors to console
             # Don't necessarily need a message here, form errors should display
             # messages.error(request, "Please correct the errors below.")

    else: # GET Request
        print("Processing GET request - displaying empty form")
        form = ResumeUploadForm()

    print("Rendering upload_resume.html template")
    return render(request, 'resumes/upload_resume.html', {'form': form})


# @login_required
# def template_selection(request):
#     """Display template options for user to select."""
#     print("==== ENTERING template_selection VIEW ====")
#
#     # Check if we're coming from resume upload
#     from_upload = request.session.get('from_resume_upload', False)
#     print(f"from_resume_upload session variable: {from_upload}")
#
#     # Debug session data (optional, can be removed in production)
#     print("Session data:")
#     for key, value in request.session.items():
#         if key == 'parsed_resume_data':
#             # Avoid printing potentially large data structure to console
#             print(f"- {key}: [data length: {len(str(value))}]")
#         # else:
#         #     print(f"- {key}: {value}") # Avoid printing sensitive keys like csrf token
#
#     # Ensure this list matches your actual template files/data
#     templates = [
#         {
#             'id': 1, 'name': 'Professional Classic',
#             'description': 'A clean and traditional format, ATS-friendly.',
#             'thumbnail': 'img/templates/1.jpg',
#             'tags': ['Classic', 'ATS-Friendly', 'Traditional']
#         },
#         {
#             'id': 2, 'name': 'Modern Minimalist',
#             'description': 'Sleek design focusing on readability and key info.',
#             'thumbnail': 'img/templates/2.jpg',
#             'tags': ['Modern', 'Minimalist', 'Clean']
#         },
#         {
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
#     ]
#
#     is_debug = getattr(settings, 'DEBUG', False) # Check if in debug mode
#
#     print(f"Rendering template_select.html with from_upload={from_upload}")
#     return render(request, 'resumes/template_select.html', {
#         'templates': templates,
#         'from_upload': from_upload,
#         'debug': is_debug # Pass debug status
#     })


@login_required
def edit_resume_section(request, resume_id, section):
    """
    Allow editing a specific section of the resume by loading data into the wizard.
    """
    print(f"==== ENTERING edit_resume_section VIEW ==== Resume ID: {resume_id}, Section: {section}")
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # Prepare form data based on the selected section
    form_data = {}
    step = None # Initialize step

    try:
        if section == 'personal':
            form_data['personal_info'] = {
                'first_name': resume.first_name, 'mid_name': resume.mid_name, 'last_name': resume.last_name,
                'email': resume.email, 'phone': resume.phone, 'address': resume.address,
                'linkedin': resume.linkedin, 'github': resume.github, 'portfolio': resume.portfolio,
            }
            step = 1
        elif section == 'summary':
            form_data['summary'] = resume.summary # Store as string directly
            step = 2
        elif section == 'skills':
            form_data['skills'] = [{'skill_name': s.skill_name, 'skill_type': s.skill_type, 'proficiency_level': s.proficiency_level} for s in resume.skills.all()]
            step = 3
        elif section == 'experience':
            form_data['experiences'] = []
            for exp in resume.experiences.all().prefetch_related('bullet_points'):
                form_data['experiences'].append({
                    'job_title': exp.job_title, 'employer': exp.employer, 'location': exp.location,
                    'start_date': exp.start_date.strftime('%Y-%m-%d') if exp.start_date else None,
                    'end_date': exp.end_date.strftime('%Y-%m-%d') if exp.end_date else None,
                    'is_current': exp.is_current,
                    'bullet_points': [{'description': bp.description} for bp in exp.bullet_points.all()],
                })
            step = 4
        elif section == 'education':
            form_data['educations'] = [{
                'school_name': edu.school_name, 'location': edu.location, 'degree': edu.degree,
                'degree_type': edu.degree_type, 'field_of_study': edu.field_of_study,
                'graduation_date': edu.graduation_date.strftime('%Y-%m-%d') if edu.graduation_date else None,
                'gpa': edu.gpa,
            } for edu in resume.educations.all()]
            step = 5
        elif section == 'projects':
             form_data['projects'] = []
             for proj in resume.projects.all().prefetch_related('bullet_points'):
                 form_data['projects'].append({
                     'project_name': proj.project_name, 'summary': proj.summary,
                     'start_date': proj.start_date.strftime('%Y-%m-%d') if proj.start_date else None,
                     'completion_date': proj.completion_date.strftime('%Y-%m-%d') if proj.completion_date else None,
                     'project_link': proj.project_link, 'github_link': proj.github_link,
                     'bullet_points': [{'description': bp.description} for bp in proj.bullet_points.all()],
                 })
             step = 6
        elif section == 'certifications':
             form_data['certifications'] = [{
                 'name': cert.name, 'institute': cert.institute,
                 'completion_date': cert.completion_date.strftime('%Y-%m-%d') if cert.completion_date else None,
                 'expiration_date': cert.expiration_date.strftime('%Y-%m-%d') if cert.expiration_date else None,
                 'score': cert.score, 'link': cert.link, 'description': cert.description,
             } for cert in resume.certifications.all()]
             step = 7
        elif section == 'languages':
            form_data['languages'] = [{'language_name': lang.language_name, 'proficiency': lang.proficiency} for lang in resume.languages.all()]
            step = 8
        elif section == 'custom':
             form_data['custom_sections'] = [{
                 'name': cust.name, 'completion_date': cust.completion_date.strftime('%Y-%m-%d') if cust.completion_date else None,
                 'bullet_points': cust.bullet_points, 'description': cust.description,
                 'link': cust.link, 'institution_name': cust.institution_name,
             } for cust in resume.custom_data.all()]
             step = 9
        else:
            print(f"ERROR: Unknown section requested for edit: {section}")
            messages.error(request, f"Invalid section '{section}' requested for editing.")
            return redirect('job_portal:view_resume', resume_id=resume.id)

        # Store data in session for the wizard
        print(f"Storing form data in session for editing section {section} (Step {step})")
        # Ensure dates are strings before storing in session if they aren't already
        # (The list comprehensions above should handle this with strftime)
        request.session['resume_form_data'] = form_data
        request.session['edit_resume_id'] = resume_id # Keep track of which resume is being edited
        request.session['resume_template_id'] = request.GET.get('template', '1') # Store template ID if needed

        # Clear upload flags if set
        if 'from_resume_upload' in request.session:
            del request.session['from_resume_upload']
        if 'parsed_resume_data' in request.session:
             del request.session['parsed_resume_data']

        # Redirect to the appropriate step in the wizard
        print(f"Redirecting to resume_wizard with step={step}")
        request.session['resume_wizard_step'] = step # Set the current step
        return redirect('job_portal:resume_wizard', step=step)

    except Exception as e:
         print(f"ERROR preparing edit section '{section}' for resume {resume_id}: {e}")
         traceback.print_exc()
         messages.error(request, f"An error occurred while preparing to edit the {section} section.")
         return redirect('job_portal:view_resume', resume_id=resume.id)


@login_required
@require_http_methods(["POST"])
def save_resume_section(request, resume_id):
    """
    Save a specific section of an edited resume.
    Note: This might be obsolete if editing redirects to the main wizard save flow.
    If kept, ensure it aligns with the wizard's data saving logic.
    """
    print(f"==== ENTERING save_resume_section VIEW ==== Resume ID: {resume_id} (Might be obsolete)")
    # Consider if this view is still needed or if edits should go through the wizard's final save
    return save_section(request, resume_id) # Delegate to the supporting code function


@login_required
def preview_upload_data(request):
    """
    Preview the data extracted from the uploaded resume.
    This view is likely temporary for debugging and might be removed later.
    """
    print("==== ENTERING preview_upload_data VIEW ====")
    parsed_data_json = request.session.get('parsed_resume_data')

    if not parsed_data_json:
        print("ERROR: No parsed_resume_data in session")
        messages.error(request, "No resume data found in session. Please upload again.")
        # Redirect to upload page instead of showing partial HTML
        return redirect('job_portal:upload_resume')

    try:
        print("Parsing JSON data from session for preview")
        parsed_data = json.loads(parsed_data_json)
        print(f"Rendering preview with {len(parsed_data.keys())} data sections")
        # Pass the template ID to the preview if available
        template_id = request.session.get('resume_template_id', 1)
        return render(request, 'resumes/preview_upload_data.html', {
            'parsed_data': parsed_data,
            'template_id': template_id # Pass template ID
        })

    except json.JSONDecodeError as json_err:
        print(f"ERROR decoding JSON for preview: {str(json_err)}")
        messages.error(request, "Error decoding preview data. The extracted data might be corrupted.")
        return redirect('job_portal:upload_resume')
    except Exception as e:
        print(f"ERROR during preview generation: {str(e)}")
        messages.error(request, f"An error occurred while generating the preview: {str(e)}")
        return redirect('job_portal:upload_resume')

