# views/project_enhancement_view.py

import time
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed # Added HttpResponseNotAllowed
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt # Or ensure CSRF token is handled correctly

from job_portal.models import APIUsage
from services.project_bullet_point_service import enhance_project_bullet_chatgpt, enhance_project_bullet_gemini


@login_required
# @require_http_methods(["POST"]) # Consider allowing only POST if GET isn't needed
# @csrf_exempt # Use only if you understand the security implications and have alternative protection
def enhance_project_bullet(request):
    """
    Enhance a single project bullet point using AI.
    This is an HTMX endpoint that returns the enhanced text, expecting POST data.
    """
    if request.method == 'POST': # Explicitly check for POST
        # --- Get parameters from request.POST ---
        bullet_text = request.POST.get('bullet_text', '')
        ai_engine = request.POST.get('ai_engine', 'chatgpt')
        enhancement_type = request.POST.get('enhancement_type', 'general')

        # Get project context parameters from POST
        # project_title = request.POST.get('project_title', '') # Removed on frontend
        project_name = request.POST.get('project_name', '')
        project_summary = request.POST.get('project_summary', '')

        # Fallback for bullet text (less common with POST, but kept for safety)
        if not bullet_text:
            for key, value in request.POST.items():
                if key.startswith('bullet_') and value: # Check request.POST here too
                    bullet_text = value
                    break

        if not bullet_text:
            return HttpResponse("<p class='text-red-500'>No bullet text found to enhance.</p>", status=400)

        # Removed project title requirement as it was removed from frontend
        # if not project_name:
        #     return HttpResponse("<p class='text-red-500'>Project name is required.</p>", status=400)

        # Start timing for API response
        start_time = time.time()

        try:
            # Choose AI engine based on user selection
            if ai_engine == 'chatgpt':
                enhanced_text, input_tokens, output_tokens = enhance_project_bullet_chatgpt(
                    bullet_text,
                    "", # Pass empty string for project_title
                    project_name,
                    project_summary,
                    enhancement_type
                )
            elif ai_engine == 'gemini':
                enhanced_text, input_tokens, output_tokens = enhance_project_bullet_gemini(
                    bullet_text,
                    "", # Pass empty string for project_title
                    project_name,
                    project_summary,
                    enhancement_type
                )
            else:
                # If no valid AI engine selected, return original text maybe with a note
                return HttpResponse(f"Unknown AI Engine. Original: {bullet_text}")

            # Calculate API response time
            response_time = time.time() - start_time

            # Log API usage (ensure this doesn't fail silently)
            try:
                usage = APIUsage(
                    user=request.user,
                    api_name=ai_engine,
                    operation='project_enhancement',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    response_time=response_time,
                    status='success'
                )
                usage.calculate_cost() # Ensure calculate_cost exists and works
                usage.save()
            except Exception as e:
                print(f"Error logging API usage: {str(e)}") # Log errors during usage logging

            # Return the enhanced text
            # Ensure the response is just the text, as HTMX will swap it directly
            enhanced_text = enhanced_text.strip()  # Optional: remove leading/trailing whitespace first
            if enhanced_text.startswith('- '):
                enhanced_text = enhanced_text[2:]
            return HttpResponse(enhanced_text)

        except Exception as e:
            print(f"Error during AI enhancement processing: {str(e)}")
            # Return a user-friendly error message
            return HttpResponse(f"<p class='text-red-500'>Sorry, an error occurred during enhancement: {e}</p>", status=500)

    else:
        # If method is not POST, explicitly return Method Not Allowed
        return HttpResponseNotAllowed(['POST'])


@login_required
def project_bullet_enhancement_form(request):
    """
    Render the project bullet enhancement form. (Seems unused by the modal flow)
    """
    # This view likely isn't used by the modal, which submits directly
    # to enhance_project_bullet via HTMX.
    return render(request, 'resumes/partials/project_ai/project_enhancement_modal.html', {
        'enhancement_type': request.GET.get('enhancement_type', 'general'),
        'ai_engine': request.GET.get('ai_engine', 'chatgpt'),
    })