import time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from ai_job_hunt_portal import settings
from job_portal.models import (
    APIUsage, JobInput
)
from services.bullets_ai_services import generate_bullets_chatgpt, get_template_bullets, generate_bullets_gemini, \
    enhance_bullet_chatgpt, enhance_bullet_gemini, enhance_bullet_basic, ats_optimize_chatgpt, ats_optimize_gemini


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