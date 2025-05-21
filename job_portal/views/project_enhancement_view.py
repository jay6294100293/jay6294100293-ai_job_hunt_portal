# job_portal/views/project_enhancement_view.py

import time
import logging
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db import transaction

from job_portal.models import APIUsage
from services.project.project_bullet_point_service import enhance_project_bullet_chatgpt, enhance_project_bullet_gemini

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def enhance_project_bullet(request):
    """
    Enhance a single project bullet point using AI.
    """
    bullet_text = request.POST.get('bullet_text', '')
    ai_engine = request.POST.get('ai_engine', 'chatgpt')
    enhancement_type = request.POST.get('enhancement_type', 'general')
    project_name = request.POST.get('project_name', '')
    project_summary = request.POST.get('project_summary', '')
    bullet_id = request.POST.get('bullet_id', '')  # Optional ID to track which bullet is being enhanced

    if not bullet_text:
        return JsonResponse({"error": "No bullet text provided to enhance."}, status=400)

    # Get API keys from user's profile
    if ai_engine == 'chatgpt':
        api_key = request.user.openai_api_key if hasattr(request.user, 'openai_api_key') else None
        if not api_key:
            return JsonResponse(
                {"error": "OpenAI API key not found. Please add your API key in your profile settings."}, status=400)
    elif ai_engine == 'gemini':
        api_key = request.user.gemini_api_key if hasattr(request.user, 'gemini_api_key') else None
        if not api_key:
            return JsonResponse(
                {"error": "Gemini API key not found. Please add your API key in your profile settings."}, status=400)
    else:
        return JsonResponse({"error": f"Unknown AI engine: {ai_engine}"}, status=400)

    start_time = time.time()
    enhanced_text = ""
    input_tokens = 0
    output_tokens = 0
    service_used = ai_engine

    try:
        with transaction.atomic():
            # Create API usage log entry with initial "pending" status
            api_usage = APIUsage.objects.create(
                user=request.user,
                api_name=service_used,
                operation='project_bullet_enhancement',
                status='pending'
            )

            # Call the enhancement service
            if ai_engine == 'chatgpt':
                enhanced_text, input_tokens, output_tokens = enhance_project_bullet_chatgpt(
                    bullet_text,
                    "",  # Empty string for project_title (no longer needed)
                    project_name,
                    project_summary,
                    enhancement_type
                )
            elif ai_engine == 'gemini':
                enhanced_text, input_tokens, output_tokens = enhance_project_bullet_gemini(
                    bullet_text,
                    "",  # Empty string for project_title (no longer needed)
                    project_name,
                    project_summary,
                    enhancement_type
                )

            response_time = time.time() - start_time
            response_time_ms = int(response_time * 1000)  # Convert to milliseconds

            # Update the API usage log with results
            is_successful = "error" not in enhanced_text.lower()

            api_usage.input_tokens = input_tokens
            api_usage.output_tokens = output_tokens
            api_usage.total_tokens = input_tokens + output_tokens
            api_usage.response_time_ms = response_time_ms
            api_usage.status = 'success' if is_successful else 'failed'

            if not is_successful:
                api_usage.error_message = enhanced_text[:200]  # Store first 200 chars of error

            # Calculate cost
            api_usage.save()  # This will trigger the cost calculation

            # Log the enhancement activity
            logger.info(
                f"Project bullet enhancement for user {request.user.username} with {service_used}, status: {api_usage.status}, tokens: {api_usage.total_tokens}"
            )

            return JsonResponse({
                "enhanced_bullet": enhanced_text,
                "ai_engine": service_used.capitalize(),
                "enhancement_type": enhancement_type,
                "bullet_id": bullet_id,  # Return the bullet ID if provided
                "tokens_used": api_usage.total_tokens,
                "cost": float(api_usage.cost) if api_usage.cost else 0.0
            })

    except Exception as e:
        logger.error(f"Error enhancing project bullet: {str(e)}", exc_info=True)
        return JsonResponse({"error": f"Error enhancing bullet: {str(e)[:100]}..."}, status=500)


@login_required
def project_bullet_enhancement_form(request):
    """
    Render the project bullet enhancement form.
    """
    # Get user API keys to check availability
    has_openai_key = bool(request.user.openai_api_key if hasattr(request.user, 'openai_api_key') else False)
    has_gemini_key = bool(request.user.gemini_api_key if hasattr(request.user, 'gemini_api_key') else False)

    return render(request, 'resumes/partials/project_ai/project_enhancement_modal.html', {
        'enhancement_type': request.GET.get('enhancement_type', 'general'),
        'ai_engine': request.GET.get('ai_engine', 'chatgpt'),
        'has_openai_key': has_openai_key,
        'has_gemini_key': has_gemini_key,
        'project_name': request.GET.get('project_name', ''),
        'project_summary': request.GET.get('project_summary', ''),
    })

# job_portal/views/project_enhancement_view.py


# # views/project_enhancement_view.py
#
# import time
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse, HttpResponseNotAllowed # Added HttpResponseNotAllowed
# from django.shortcuts import render
#
# from job_portal.models import APIUsage
# from services.project.project_bullet_point_service import enhance_project_bullet_chatgpt, enhance_project_bullet_gemini
#
#
# @login_required
# # @require_http_methods(["POST"]) # Consider allowing only POST if GET isn't needed
# # @csrf_exempt # Use only if you understand the security implications and have alternative protection
# def enhance_project_bullet(request):
#     """
#     Enhance a single project bullet point using AI.
#     This is an HTMX endpoint that returns the enhanced text, expecting POST data.
#     """
#     if request.method == 'POST': # Explicitly check for POST
#         # --- Get parameters from request.POST ---
#         bullet_text = request.POST.get('bullet_text', '')
#         ai_engine = request.POST.get('ai_engine', 'chatgpt')
#         enhancement_type = request.POST.get('enhancement_type', 'general')
#
#         # Get project context parameters from POST
#         # project_title = request.POST.get('project_title', '') # Removed on frontend
#         project_name = request.POST.get('project_name', '')
#         project_summary = request.POST.get('project_summary', '')
#
#         # Fallback for bullet text (less common with POST, but kept for safety)
#         if not bullet_text:
#             for key, value in request.POST.items():
#                 if key.startswith('bullet_') and value: # Check request.POST here too
#                     bullet_text = value
#                     break
#
#         if not bullet_text:
#             return HttpResponse("<p class='text-red-500'>No bullet text found to enhance.</p>", status=400)
#
#         # Removed project title requirement as it was removed from frontend
#         # if not project_name:
#         #     return HttpResponse("<p class='text-red-500'>Project name is required.</p>", status=400)
#
#         # Start timing for API response
#         start_time = time.time()
#
#         try:
#             # Choose AI engine based on user selection
#             if ai_engine == 'chatgpt':
#                 enhanced_text, input_tokens, output_tokens = enhance_project_bullet_chatgpt(
#                     bullet_text,
#                     "", # Pass empty string for project_title
#                     project_name,
#                     project_summary,
#                     enhancement_type
#                 )
#             elif ai_engine == 'gemini':
#                 enhanced_text, input_tokens, output_tokens = enhance_project_bullet_gemini(
#                     bullet_text,
#                     "", # Pass empty string for project_title
#                     project_name,
#                     project_summary,
#                     enhancement_type
#                 )
#             else:
#                 # If no valid AI engine selected, return original text maybe with a note
#                 return HttpResponse(f"Unknown AI Engine. Original: {bullet_text}")
#
#             # Calculate API response time
#             response_time = time.time() - start_time
#
#             # Log API usage (ensure this doesn't fail silently)
#             try:
#                 usage = APIUsage(
#                     user=request.user,
#                     api_name=ai_engine,
#                     operation='project_enhancement',
#                     input_tokens=input_tokens,
#                     output_tokens=output_tokens,
#                     response_time=response_time,
#                     status='success'
#                 )
#                 usage.calculate_cost() # Ensure calculate_cost exists and works
#                 usage.save()
#             except Exception as e:
#                 print(f"Error logging API usage: {str(e)}") # Log errors during usage logging
#
#             # Return the enhanced text
#             # Ensure the response is just the text, as HTMX will swap it directly
#             enhanced_text = enhanced_text.strip()  # Optional: remove leading/trailing whitespace first
#             if enhanced_text.startswith('- '):
#                 enhanced_text = enhanced_text[2:]
#             return HttpResponse(enhanced_text)
#
#         except Exception as e:
#             print(f"Error during AI enhancement processing: {str(e)}")
#             # Return a user-friendly error message
#             return HttpResponse(f"<p class='text-red-500'>Sorry, an error occurred during enhancement: {e}</p>", status=500)
#
#     else:
#         # If method is not POST, explicitly return Method Not Allowed
#         return HttpResponseNotAllowed(['POST'])
#
#
# @login_required
# def project_bullet_enhancement_form(request):
#     """
#     Render the project bullet enhancement form. (Seems unused by the modal flow)
#     """
#     # This view likely isn't used by the modal, which submits directly
#     # to enhance_project_bullet via HTMX.
#     return render(request, 'resumes/partials/project_ai/project_enhancement_modal.html', {
#         'enhancement_type': request.GET.get('enhancement_type', 'general'),
#         'ai_engine': request.GET.get('ai_engine', 'chatgpt'),
#     })