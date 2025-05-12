# job_portal/views/experience_enhancement_view.py
import time
import logging
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from ai_job_hunt_portal import settings
from job_portal.models import APIUsage

from services.bullets_ai_services import (
    generate_bullets_chatgpt,
    get_template_bullets,
    generate_bullets_gemini,
    enhance_bullet_chatgpt,
    enhance_bullet_gemini,
    enhance_bullet_basic,
)

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def ai_generate_bullets(request):
    """
    Generate bullet points for an experience entry using either ChatGPT or Gemini.
    This endpoint returns HTML fragments for each bullet point.
    'employer' field is no longer used in this process.
    """
    job_title = request.GET.get('job_title')
    parent_index = request.GET.get('parent_index', '0')
    ai_engine = request.GET.get('ai_engine', 'chatgpt')

    # Enhanced parameters (still useful for context)
    target_job_title = request.GET.get('target_job_title')
    skills = request.GET.get('skills')
    responsibilities = request.GET.get('responsibilities')

    try:
        bullet_count_str = request.GET.get('bullet_count', '3')
        bullet_count = int(bullet_count_str)
        # Ensure bullet_count is within a reasonable range, e.g., 1 to 5
        bullet_count = min(max(bullet_count, 1), 5)
    except ValueError:
        bullet_count = 3  # Default if conversion fails or param is invalid

    # MODIFIED: Only job_title is strictly required for this endpoint now
    if not job_title or not job_title.strip():
        logger.warning("ai_generate_bullets called without a valid job_title.")
        return HttpResponse("Job title is required to generate bullets.", status=400)

    start_time = time.time()
    bullets = []
    input_tokens = 0
    output_tokens = 0
    service_used = "template"  # Default if no AI is used or AI fails

    # MODIFIED: Pass employer=None to the service functions
    if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
        service_used = "chatgpt"
        logger.info(f"Attempting to generate {bullet_count} bullets for '{job_title}' using ChatGPT.")
        bullets, input_tokens, output_tokens = generate_bullets_chatgpt(
            job_title=job_title,
            employer=None,  # Employer is now explicitly None
            target_job_title=target_job_title,
            skills=skills,
            responsibilities=responsibilities,
            num_bullets=bullet_count
        )
    elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
        service_used = "gemini"
        logger.info(f"Attempting to generate {bullet_count} bullets for '{job_title}' using Gemini.")
        bullets, input_tokens, output_tokens = generate_bullets_gemini(
            job_title=job_title,
            employer=None,  # Employer is now explicitly None
            target_job_title=target_job_title,
            skills=skills,
            responsibilities=responsibilities,
            num_bullets=bullet_count
        )
    else:
        if not settings.OPENAI_API_KEY and not settings.GOOGLE_GENAI_API_KEY:
            logger.info("No AI API keys configured. Falling back to template bullets for job: %s", job_title)
        else:
            logger.info(
                "Selected AI engine '%s' not configured or API key missing. Falling back to template bullets for job: %s",
                ai_engine, job_title)

        bullets = get_template_bullets(
            job_title=job_title,
            employer=None,  # Employer is now explicitly None
            num_bullets=bullet_count
        )
        # input_tokens, output_tokens remain 0 for template

    response_time = time.time() - start_time
    logger.info(
        f"Bullet generation for '{job_title}' using {service_used} took {response_time:.2f}s. Generated {len(bullets)} bullets.")

    # Log API usage if an AI service was successfully invoked
    if service_used in ["chatgpt", "gemini"]:
        try:
            # Determine status based on whether actual bullet content was returned
            is_successful_generation = any(
                "error" not in b.lower() and
                "could not generate" not in b.lower() and
                "api key not configured" not in b.lower() and
                "blocked by gemini" not in b.lower()
                for b in bullets
            )

            usage_status = 'success' if is_successful_generation and bullets else 'failure_ai_response'

            usage = APIUsage(
                user=request.user,
                api_name=service_used,
                operation='experience_bullet_generation',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time=response_time,
                status=usage_status
            )
            if hasattr(usage, 'calculate_cost'):  # Check if method exists
                usage.calculate_cost()
            usage.save()
            logger.info(
                f"API usage logged for user {request.user.username}, service: {service_used}, status: {usage_status}")
        except Exception as e:
            logger.error(f"Error logging API usage for {service_used}: {str(e)}", exc_info=True)

    bullet_html_list = []
    if bullets:  # Check if bullets list is not empty
        for idx, bullet_text in enumerate(bullets):
            if not isinstance(bullet_text, str):  # Ensure bullet_text is a string
                bullet_text = "Error: Received invalid bullet format from AI."
                logger.warning(
                    f"Non-string bullet content received: {bullet_text} for job_title: {job_title}, index: {idx}")

            # Render each bullet point to HTML
            try:
                html_for_bullet = render_to_string(
                    'resumes/partials/experience_ai/experience_bullet_point_form_row.html', {
                        'parent_index': parent_index,
                        'index': idx,
                        'bullet_text': bullet_text.strip(),  # Ensure text is stripped
                    })
                bullet_html_list.append(html_for_bullet)
            except Exception as e_render:
                logger.error(f"Error rendering bullet template for '{bullet_text}': {e_render}", exc_info=True)
                bullet_html_list.append(
                    f"<div class='text-red-500 p-2'>Error rendering bullet: {bullet_text[:50]}...</div>")

    if not bullet_html_list:
        logger.info("No valid bullet HTML was generated to return for job_title: %s", job_title)
        return HttpResponse("", status=200)

    return HttpResponse("".join(bullet_html_list))


@login_required
@require_http_methods(["GET"])
def enhance_bullet(request):
    """
    Enhance a single bullet point using AI.
    Returns JSON response with the enhanced bullet text.
    """
    bullet_text = request.GET.get('bullet_text', '')
    ai_engine = request.GET.get('ai_engine', 'chatgpt')
    enhancement_type = request.GET.get('enhancement_type', 'general')

    if not bullet_text or not bullet_text.strip():
        logger.warning("enhance_bullet called with empty bullet_text.")
        return JsonResponse({"error": "No bullet text provided to enhance."}, status=400)

    start_time = time.time()
    enhanced_text = ""
    input_tokens = 0
    output_tokens = 0
    service_used = "basic"  # Default

    try:
        if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
            service_used = "chatgpt"
            enhanced_text, input_tokens, output_tokens = enhance_bullet_chatgpt(
                bullet_text, enhancement_type
            )
        elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
            service_used = "gemini"
            enhanced_text, input_tokens, output_tokens = enhance_bullet_gemini(
                bullet_text, enhancement_type
            )
        else:
            if not settings.OPENAI_API_KEY and not settings.GOOGLE_GENAI_API_KEY:
                logger.info("No AI API keys for enhancement. Falling back to basic enhancement.")
            else:
                logger.info(
                    "Selected AI engine '%s' for enhancement not configured/API key missing. Falling back to basic.",
                    ai_engine)
            enhanced_text = enhance_bullet_basic(bullet_text)
            service_used = "basic"

        response_time = time.time() - start_time
        logger.info(f"Bullet enhancement using {service_used} took {response_time:.2f}s.")

        # Log API usage
        if service_used in ["chatgpt", "gemini"]:
            try:
                is_successful_enhancement = "error" not in enhanced_text.lower() and \
                                            "blocked by gemini" not in enhanced_text.lower() and \
                                            "api key not configured" not in enhanced_text.lower()

                usage_status = 'success' if is_successful_enhancement else 'failure_ai_response'

                usage = APIUsage(
                    user=request.user,
                    api_name=service_used,
                    operation='bullet_enhancement',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    response_time=response_time,
                    status=usage_status
                )
                if hasattr(usage, 'calculate_cost'):
                    usage.calculate_cost()
                usage.save()
                logger.info(
                    f"API usage logged for bullet enhancement: user {request.user.username}, service: {service_used}, status: {usage_status}")
            except Exception as e:
                logger.error(f"Error logging API usage for enhancement ({service_used}): {str(e)}", exc_info=True)

        # Return JSON response
        return JsonResponse({
            "enhanced_bullet": enhanced_text,
            "ai_engine": service_used.capitalize(),
            "enhancement_type": enhancement_type
        })

    except Exception as e:
        logger.error(f"Error in enhance_bullet: {str(e)}", exc_info=True)
        return JsonResponse({"error": f"Error enhancing bullet: {str(e)[:100]}..."}, status=500)


@login_required
@require_http_methods(["GET"])
def check_bullet_strength(request):
    """
    Evaluate the strength of a bullet point and provide feedback as an HTML snippet.
    """
    bullet_text = request.GET.get('bullet_text', '')
    if not bullet_text or not bullet_text.strip():
        return HttpResponse("")

    score = 0
    feedback_items = []

    # Comprehensive list of action verbs (can be expanded)
    action_verbs = [
        "Achieved", "Accelerated", "Administered", "Advised", "Analyzed", "Authored", "Automated",
        "Balanced", "Budgeted", "Built", "Calculated", "Centralized", "Chaired", "Championed",
        "Coached", "Collaborated", "Communicated", "Conceived", "Conceptualized", "Consolidated",
        "Constructed", "Consulted", "Contracted", "Controlled", "Coordinated", "Counseled",
        "Created", "Cultivated", "Cut", "Decreased", "Defined", "Delivered", "Demonstrated",
        "Designed", "Detected", "Developed", "Devised", "Directed", "Discovered", "Distributed",
        "Documented", "Doubled", "Drafted", "Edited", "Educated", "Eliminated", "Enabled",
        "Enforced", "Engineered", "Enhanced", "Ensured", "Established", "Estimated", "Evaluated",
        "Examined", "Executed", "Expanded", "Expedited", "Facilitated", "Finalized", "Financed",
        "Forecasted", "Formulated", "Founded", "Generated", "Guided", "Halved", "Headed",
        "Identified", "Implemented", "Improved", "Improvised", "Increased", "Influenced",
        "Initiated", "Innovated", "Inspected", "Inspired", "Installed", "Instituted", "Instructed",
        "Integrated", "Interpreted", "Interviewed", "Invented", "Launched", "Led", "Leveraged",
        "Lobbied", "Maintained", "Managed", "Marketed", "Maximized", "Measured", "Mediated",
        "Mentored", "Minimized", "Mobilized", "Modeled", "Monitored", "Motivated", "Negotiated",
        "Operated", "Orchestrated", "Organized", "Overhauled", "Oversaw", "Participated",
        "Partnered", "Performed", "Persuaded", "Pioneered", "Planned", "Predicted", "Prepared",
        "Presented", "Presided", "Prioritized", "Produced", "Programmed", "Projected", "Promoted",
        "Proposed", "Proved", "Provided", "Published", "Purchased", "Qualified", "Quantified",
        "Ran", "Rated", "Realized", "Recommended", "Reconciled", "Recorded", "Recruited",
        "Redesigned", "Reduced", "Re-engineered", "Regulated", "Rehabilitated", "Reinforced",
        "Remodeled", "Reorganized", "Repaired", "Reported", "Represented", "Researched",
        "Resolved", "Restored", "Restructured", "Retained", "Retrieved", "Revamped", "Reviewed",
        "Revised", "Revitalized", "Saved", "Scheduled", "Screened", "Secured", "Selected",
        "Serviced", "Shaped", "Simplified", "Sold", "Solved", "Sourced", "Spearheaded",
        "Specified", "Standardized", "Steered", "Stimulated", "Streamlined", "Strengthened",
        "Structured", "Studied", "Summarized", "Supervised", "Supplied", "Supported", "Surveyed",
        "Synthesized", "Systematized", "Tabulated", "Tailored", "Taught", "Tested", "Traded",
        "Trained", "Transformed", "Translated", "Traveled", "Treated", "Trimmed", "Tripled",
        "Troubleshot", "Tutored", "Uncovered", "Unified", "United", "Updated", "Upgraded",
        "Utilized", "Validated", "Valued", "Visualized", "Volunteered", "Won", "Wrote"
    ]

    first_word = bullet_text.split(" ")[0].strip().rstrip(',')  # Get first word, remove trailing comma
    if any(first_word.lower() == verb.lower() for verb in action_verbs):
        score += 2
    else:
        feedback_items.append("Start with a strong action verb")

    if any(c.isdigit() for c in bullet_text) or '%' in bullet_text or '$' in bullet_text:
        score += 2
        if '%' in bullet_text or '$' in bullet_text or any(char.isdigit() and char not in '01' for char in bullet_text):
            score += 1
    else:
        feedback_items.append("Add measurable results (e.g., numbers, %, $)")

    # Length check
    length = len(bullet_text)
    if 70 <= length <= 200:  # Optimal range
        score += 2
    elif length < 50:
        feedback_items.append("Too brief - expand with more details")
    elif length > 250:
        feedback_items.append("Too lengthy - try to be more concise")
    else:  # Okay length, but not optimal
        score += 1

    rating_text = "Needs Improvement"
    color_class = "text-red-600"
    stars = "★★☆☆☆"

    if score >= 6:
        rating_text = "Excellent!"
        color_class = "text-green-600"
        stars = "★★★★★"
    elif score >= 4:
        rating_text = "Good"
        color_class = "text-yellow-600"
        stars = "★★★★☆"
    elif score >= 2:
        rating_text = "Average"
        color_class = "text-yellow-500"
        stars = "★★★☆☆"

    result_html = f'<div class="flex items-center text-sm"><span class="{color_class} font-semibold">{rating_text}&nbsp;{stars}</span>'
    if feedback_items:
        result_html += f'<span class="text-gray-500 ml-2">Tip: {feedback_items[0]}.</span>'
    result_html += '</div>'

    return HttpResponse(result_html)

# # job_portal/views/experience_enhancement_view.py
# import time
# import logging  # It's good practice to use logging
#
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from django.views.decorators.http import require_http_methods
#
# from ai_job_hunt_portal import settings  # For API keys and model names
# from job_portal.models import APIUsage
# # Assuming JobInput is not used in this specific view's functions
# # from job_portal.models import JobInput
#
# from services.bullets_ai_services import (
#     generate_bullets_chatgpt,
#     get_template_bullets,
#     generate_bullets_gemini,
#     enhance_bullet_chatgpt,
#     enhance_bullet_gemini,
#     enhance_bullet_basic,
#     # ats_optimize_chatgpt, # Keep if you use ATS optimization elsewhere from this view
#     # ats_optimize_gemini
# )
#
# logger = logging.getLogger(__name__)
#
#
# @login_required
# @require_http_methods(["GET"])
# def ai_generate_bullets(request):
#     """
#     Generate bullet points for an experience entry using either ChatGPT or Gemini.
#     This endpoint returns HTML fragments for each bullet point.
#     'employer' field is no longer used in this process.
#     """
#     job_title = request.GET.get('job_title')
#     # employer = request.GET.get('employer') # REMOVED - employer is no longer taken from request
#
#     parent_index = request.GET.get('parent_index', '0')  # For client-side context if template needs it
#     ai_engine = request.GET.get('ai_engine', 'chatgpt')
#
#     # Enhanced parameters (still useful for context)
#     target_job_title = request.GET.get('target_job_title')
#     skills = request.GET.get('skills')
#     responsibilities = request.GET.get('responsibilities')
#
#     try:
#         bullet_count_str = request.GET.get('bullet_count', '3')
#         bullet_count = int(bullet_count_str)
#         # Ensure bullet_count is within a reasonable range, e.g., 1 to 5
#         bullet_count = min(max(bullet_count, 1), 5)
#     except ValueError:
#         bullet_count = 3  # Default if conversion fails or param is invalid
#
#     # MODIFIED: Only job_title is strictly required for this endpoint now
#     if not job_title or not job_title.strip():
#         logger.warning("ai_generate_bullets called without a valid job_title.")
#         return HttpResponse("Job title is required to generate bullets.", status=400)
#
#     start_time = time.time()
#     bullets = []
#     input_tokens = 0
#     output_tokens = 0
#     service_used = "template"  # Default if no AI is used or AI fails
#
#     # MODIFIED: Pass employer=None to the service functions
#     if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
#         service_used = "chatgpt"
#         logger.info(f"Attempting to generate {bullet_count} bullets for '{job_title}' using ChatGPT.")
#         bullets, input_tokens, output_tokens = generate_bullets_chatgpt(
#             job_title=job_title,
#             employer=None,  # Employer is now explicitly None
#             target_job_title=target_job_title,
#             skills=skills,
#             responsibilities=responsibilities,
#             num_bullets=bullet_count
#         )
#     elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
#         service_used = "gemini"
#         logger.info(f"Attempting to generate {bullet_count} bullets for '{job_title}' using Gemini.")
#         bullets, input_tokens, output_tokens = generate_bullets_gemini(
#             job_title=job_title,
#             employer=None,  # Employer is now explicitly None
#             target_job_title=target_job_title,
#             skills=skills,
#             responsibilities=responsibilities,
#             num_bullets=bullet_count
#         )
#     else:
#         if not settings.OPENAI_API_KEY and not settings.GOOGLE_GENAI_API_KEY:
#             logger.info("No AI API keys configured. Falling back to template bullets for job: %s", job_title)
#         else:
#             logger.info(
#                 "Selected AI engine '%s' not configured or API key missing. Falling back to template bullets for job: %s",
#                 ai_engine, job_title)
#
#         bullets = get_template_bullets(
#             job_title=job_title,
#             employer=None,  # Employer is now explicitly None
#             num_bullets=bullet_count
#         )
#         # input_tokens, output_tokens remain 0 for template
#
#     response_time = time.time() - start_time
#     logger.info(
#         f"Bullet generation for '{job_title}' using {service_used} took {response_time:.2f}s. Generated {len(bullets)} bullets.")
#
#     # Log API usage if an AI service was successfully invoked (even if it returned error messages in bullets list)
#     if service_used in ["chatgpt", "gemini"]:
#         try:
#             # Determine status based on whether actual bullet content was returned (not error messages)
#             # This is a basic check; more robust error handling might be in the service layer.
#             is_successful_generation = any(
#                 "error" not in b.lower() and
#                 "could not generate" not in b.lower() and
#                 "api key not configured" not in b.lower() and
#                 "blocked by gemini" not in b.lower()
#                 for b in bullets
#             )
#
#             usage_status = 'success' if is_successful_generation and bullets else 'failure_ai_response'
#
#             usage = APIUsage(
#                 user=request.user,
#                 api_name=service_used,
#                 operation='experience_bullet_generation',
#                 input_tokens=input_tokens,
#                 output_tokens=output_tokens,
#                 response_time=response_time,
#                 status=usage_status
#             )
#             if hasattr(usage, 'calculate_cost'):  # Check if method exists
#                 usage.calculate_cost()
#             usage.save()
#             logger.info(
#                 f"API usage logged for user {request.user.username}, service: {service_used}, status: {usage_status}")
#         except Exception as e:
#             logger.error(f"Error logging API usage for {service_used}: {str(e)}", exc_info=True)
#
#     bullet_html_list = []
#     if bullets:  # Check if bullets list is not empty
#         for idx, bullet_text in enumerate(bullets):
#             if not isinstance(bullet_text, str):  # Ensure bullet_text is a string
#                 bullet_text = "Error: Received invalid bullet format from AI."
#                 logger.warning(
#                     f"Non-string bullet content received: {bullet_text} for job_title: {job_title}, index: {idx}")
#
#             # Render each bullet point to HTML
#             # The template path is 'resumes/partials/experience_ai/experience_bullet_point_form_row.html'
#             # as per your uploaded file structure.
#             try:
#                 html_for_bullet = render_to_string(
#                     'resumes/partials/experience_ai/experience_bullet_point_form_row.html', {
#                         'parent_index': parent_index,
#                         'index': idx,
#                         'bullet_text': bullet_text.strip(),  # Ensure text is stripped
#                     })
#                 bullet_html_list.append(html_for_bullet)
#             except Exception as e_render:
#                 logger.error(f"Error rendering bullet template for '{bullet_text}': {e_render}", exc_info=True)
#                 # Optionally append an error placeholder to the HTML list
#                 bullet_html_list.append(
#                     f"<div class='text-red-500 p-2'>Error rendering bullet: {bullet_text[:50]}...</div>")
#
#     if not bullet_html_list:
#         logger.info("No valid bullet HTML was generated to return for job_title: %s", job_title)
#         # Return an empty string with 200 OK, client-side JS can handle this as "no bullets generated"
#         return HttpResponse("", status=200)
#
#     return HttpResponse("".join(bullet_html_list))
#
#
# @login_required
# @require_http_methods(["GET"])
# def enhance_bullet(request):
#     """
#     Enhance a single bullet point using AI.
#     'employer' is not directly relevant here unless it's part of context like job_description.
#     """
#     bullet_text = request.GET.get('bullet_text', '')
#     ai_engine = request.GET.get('ai_engine', 'chatgpt')
#     enhancement_type = request.GET.get('enhancement_type', 'general')
#     job_description = request.GET.get('job_description', '')  # For ATS optimization context
#     job_title_context = request.GET.get('job_title_context', '')  # Job title for context if needed
#
#     # This ID helps the client-side JS identify which bullet's text to update
#     bullet_id_on_form = request.GET.get('bullet_id_on_form', '')
#
#     if not bullet_text or not bullet_text.strip():
#         logger.warning("enhance_bullet called with empty bullet_text.")
#         return HttpResponse("No bullet text provided to enhance.", status=400)
#
#     start_time = time.time()
#     enhanced_text = "Enhancement service unavailable or an error occurred."
#     input_tokens = 0
#     output_tokens = 0
#     service_used = "basic"  # Default
#
#     if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
#         service_used = "chatgpt"
#         enhanced_text, input_tokens, output_tokens = enhance_bullet_chatgpt(
#             bullet_text, enhancement_type, job_description
#         )
#     elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
#         service_used = "gemini"
#         enhanced_text, input_tokens, output_tokens = enhance_bullet_gemini(
#             bullet_text, enhancement_type, job_description
#         )
#     else:
#         if not settings.OPENAI_API_KEY and not settings.GOOGLE_GENAI_API_KEY:
#             logger.info("No AI API keys for enhancement. Falling back to basic enhancement.")
#         else:
#             logger.info(
#                 "Selected AI engine '%s' for enhancement not configured/API key missing. Falling back to basic.",
#                 ai_engine)
#         enhanced_text = enhance_bullet_basic(bullet_text)
#
#     response_time = time.time() - start_time
#     logger.info(f"Bullet enhancement using {service_used} took {response_time:.2f}s.")
#
#     if service_used in ["chatgpt", "gemini"]:
#         try:
#             is_successful_enhancement = "error" not in enhanced_text.lower() and \
#                                         "blocked by gemini" not in enhanced_text.lower() and \
#                                         "api key not configured" not in enhanced_text.lower()
#
#             usage_status = 'success' if is_successful_enhancement else 'failure_ai_response'
#
#             usage = APIUsage(
#                 user=request.user,
#                 api_name=service_used,
#                 operation='bullet_enhancement',
#                 input_tokens=input_tokens,
#                 output_tokens=output_tokens,
#                 response_time=response_time,
#                 status=usage_status
#             )
#             if hasattr(usage, 'calculate_cost'):
#                 usage.calculate_cost()
#             usage.save()
#             logger.info(
#                 f"API usage logged for bullet enhancement: user {request.user.username}, service: {service_used}, status: {usage_status}")
#         except Exception as e:
#             logger.error(f"Error logging API usage for enhancement ({service_used}): {str(e)}", exc_info=True)
#
#     # For HTMX, you might return an HTML snippet here.
#     # For direct JS fetch, returning JSON is often cleaner.
#     # Given your ai_generate_bullets returns HTML, consistency might be to return HTML here too.
#     # However, the original code returned plain text for enhanced_bullet.
#     # Let's stick to plain text for now, or consider JSON if more data needs to go back.
#     # If using JSON:
#     # from django.http import JsonResponse
#     # return JsonResponse({'enhanced_text': enhanced_text, 'bullet_id_on_form': bullet_id_on_form})
#     return HttpResponse(enhanced_text)
#
#
# @login_required
# @require_http_methods(["GET"])
# def check_bullet_strength(request):
#     """
#     Evaluate the strength of a bullet point and provide feedback as an HTML snippet.
#     """
#     bullet_text = request.GET.get('bullet_text', '')
#     if not bullet_text or not bullet_text.strip():
#         return HttpResponse("")
#
#     score = 0
#     feedback_items = []
#
#     # Comprehensive list of action verbs (can be expanded)
#     action_verbs = [
#         "Achieved", "Accelerated", "Administered", "Advised", "Analyzed", "Authored", "Automated",
#         "Balanced", "Budgeted", "Built", "Calculated", "Centralized", "Chaired", "Championed",
#         "Coached", "Collaborated", "Communicated", "Conceived", "Conceptualized", "Consolidated",
#         "Constructed", "Consulted", "Contracted", "Controlled", "Coordinated", "Counseled",
#         "Created", "Cultivated", "Cut", "Decreased", "Defined", "Delivered", "Demonstrated",
#         "Designed", "Detected", "Developed", "Devised", "Directed", "Discovered", "Distributed",
#         "Documented", "Doubled", "Drafted", "Edited", "Educated", "Eliminated", "Enabled",
#         "Enforced", "Engineered", "Enhanced", "Ensured", "Established", "Estimated", "Evaluated",
#         "Examined", "Executed", "Expanded", "Expedited", "Facilitated", "Finalized", "Financed",
#         "Forecasted", "Formulated", "Founded", "Generated", "Guided", "Halved", "Headed",
#         "Identified", "Implemented", "Improved", "Improvised", "Increased", "Influenced",
#         "Initiated", "Innovated", "Inspected", "Inspired", "Installed", "Instituted", "Instructed",
#         "Integrated", "Interpreted", "Interviewed", "Invented", "Launched", "Led", "Leveraged",
#         "Lobbied", "Maintained", "Managed", "Marketed", "Maximized", "Measured", "Mediated",
#         "Mentored", "Minimized", "Mobilized", "Modeled", "Monitored", "Motivated", "Negotiated",
#         "Operated", "Orchestrated", "Organized", "Overhauled", "Oversaw", "Participated",
#         "Partnered", "Performed", "Persuaded", "Pioneered", "Planned", "Predicted", "Prepared",
#         "Presented", "Presided", "Prioritized", "Produced", "Programmed", "Projected", "Promoted",
#         "Proposed", "Proved", "Provided", "Published", "Purchased", "Qualified", "Quantified",
#         "Ran", "Rated", "Realized", "Recommended", "Reconciled", "Recorded", "Recruited",
#         "Redesigned", "Reduced", "Re-engineered", "Regulated", "Rehabilitated", "Reinforced",
#         "Remodeled", "Reorganized", "Repaired", "Reported", "Represented", "Researched",
#         "Resolved", "Restored", "Restructured", "Retained", "Retrieved", "Revamped", "Reviewed",
#         "Revised", "Revitalized", "Saved", "Scheduled", "Screened", "Secured", "Selected",
#         "Serviced", "Shaped", "Simplified", "Sold", "Solved", "Sourced", "Spearheaded",
#         "Specified", "Standardized", "Steered", "Stimulated", "Streamlined", "Strengthened",
#         "Structured", "Studied", "Summarized", "Supervised", "Supplied", "Supported", "Surveyed",
#         "Synthesized", "Systematized", "Tabulated", "Tailored", "Taught", "Tested", "Traded",
#         "Trained", "Transformed", "Translated", "Traveled", "Treated", "Trimmed", "Tripled",
#         "Troubleshot", "Tutored", "Uncovered", "Unified", "United", "Updated", "Upgraded",
#         "Utilized", "Validated", "Valued", "Visualized", "Volunteered", "Won", "Wrote"
#     ]
#
#     first_word = bullet_text.split(" ")[0].strip().rstrip(',')  # Get first word, remove trailing comma
#     if any(first_word.lower() == verb.lower() for verb in action_verbs):
#         score += 2
#     else:
#         feedback_items.append("Start with a strong action verb")
#
#     if any(c.isdigit() for c in bullet_text) or '%' in bullet_text or '$' in bullet_text:
#         score += 2
#         if '%' in bullet_text or '$' in bullet_text or any(char.isdigit() and char not in '01' for char in bullet_text):
#             score += 1
#     else:
#         feedback_items.append("Add measurable results (e.g., numbers, %, $)")
#
#     # Length check
#     length = len(bullet_text)
#     if 70 <= length <= 200:  # Optimal range
#         score += 2
#     elif length < 50:
#         feedback_items.append("Too brief - expand with more details")
#     elif length > 250:
#         feedback_items.append("Too lengthy - try to be more concise")
#     else:  # Okay length, but not optimal
#         score += 1
#
#     rating_text = "Needs Improvement"
#     color_class = "text-red-600"
#     stars = "★★☆☆☆"
#
#     if score >= 6:
#         rating_text = "Excellent!"
#         color_class = "text-green-600"
#         stars = "★★★★★"
#     elif score >= 4:
#         rating_text = "Good"
#         color_class = "text-yellow-600"
#         stars = "★★★★☆"
#     elif score >= 2:
#         rating_text = "Average"
#         color_class = "text-yellow-500"
#         stars = "★★★☆☆"
#
#     result_html = f'<div class="flex items-center text-sm"><span class="{color_class} font-semibold">{rating_text}&nbsp;{stars}</span>'
#     if feedback_items:
#         result_html += f'<span class="text-gray-500 ml-2">Tip: {feedback_items[0]}.</span>'
#     result_html += '</div>'
#
#     return HttpResponse(result_html)
#
# # import time
# #
# # from django.contrib.auth.decorators import login_required
# # from django.http import HttpResponse
# # from django.template.loader import render_to_string
# # from django.views.decorators.http import require_http_methods
# #
# # from ai_job_hunt_portal import settings
# # from job_portal.models import (
# #     APIUsage, JobInput
# # )
# # from services.bullets_ai_services import generate_bullets_chatgpt, get_template_bullets, generate_bullets_gemini, \
# #     enhance_bullet_chatgpt, enhance_bullet_gemini, enhance_bullet_basic, ats_optimize_chatgpt, ats_optimize_gemini
# #
# #
# # @login_required
# # @require_http_methods(["GET"])
# # def ai_generate_bullets(request):
# #     """
# #     Generate bullet points based on job information using either ChatGPT or Gemini.
# #     This is an HTMX endpoint that returns HTML for the bullet points.
# #     """
# #     job_title = request.GET.get('job_title')
# #     employer = request.GET.get('employer')
# #     parent_index = request.GET.get('parent_index', '0')
# #     ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Default to ChatGPT
# #
# #     # Enhanced parameters
# #     target_job_title = request.GET.get('target_job_title')
# #     skills = request.GET.get('skills')
# #     responsibilities = request.GET.get('responsibilities')
# #
# #     # New parameter for number of bullet points requested
# #     bullet_count = int(request.GET.get('bullet_count', 3))
# #     # Ensure the count is between 1 and 5
# #     bullet_count = min(max(bullet_count, 1), 5)
# #
# #     if not job_title or not employer:
# #         return HttpResponse("Job title and employer are required", status=400)
# #
# #     # Start timing for API response
# #     start_time = time.time()
# #
# #     # Choose AI engine based on user selection
# #     if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
# #         bullets, input_tokens, output_tokens = generate_bullets_chatgpt(
# #             job_title,
# #             employer,
# #             target_job_title,
# #             skills,
# #             responsibilities,
# #             bullet_count  # Pass the bullet count to the AI function
# #         )
# #     elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
# #         bullets, input_tokens, output_tokens = generate_bullets_gemini(
# #             job_title,
# #             employer,
# #             target_job_title,
# #             skills,
# #             responsibilities,
# #             bullet_count  # Pass the bullet count to the AI function
# #         )
# #     else:
# #         # Fallback to template-based generation with specified count
# #         bullets = get_template_bullets(job_title, employer, bullet_count)
# #         input_tokens = output_tokens = 0
# #
# #     # Calculate API response time
# #     response_time = time.time() - start_time
# #
# #     # Log API usage if using AI
# #     if (ai_engine == 'chatgpt' and settings.OPENAI_API_KEY) or (
# #             ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY):
# #         try:
# #             # Create API usage record
# #             usage = APIUsage(
# #                 user=request.user,
# #                 api_name=ai_engine,
# #                 operation='content_generation',
# #                 input_tokens=input_tokens,
# #                 output_tokens=output_tokens,
# #                 response_time=response_time,
# #                 status='success'
# #             )
# #             usage.calculate_cost()
# #             usage.save()
# #         except Exception as e:
# #             print(f"Error logging API usage: {str(e)}")
# #
# #     # Render the bullet points to HTML
# #     bullet_html = ''
# #     for idx, bullet_text in enumerate(bullets):
# #         bullet_html += render_to_string('resumes/partials/bullet_point_form_row.html', {
# #             'parent_index': parent_index,
# #             'index': idx,
# #             'bullet_text': bullet_text,
# #         })
# #
# #     # Return the HTML
# #     return HttpResponse(bullet_html)
# #
# # @login_required
# # @require_http_methods(["GET"])
# # def enhance_bullet(request):
# #     """
# #     Enhance a single bullet point using AI.
# #     This is an HTMX endpoint that returns the enhanced text.
# #     """
# #     bullet_text = request.GET.get('bullet_text', '')
# #     ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Default to ChatGPT
# #     enhancement_type = request.GET.get('enhancement_type', 'general')
# #     job_description = request.GET.get('job_description', '')
# #
# #     # Try to get text from the included textarea if not provided directly
# #     if not bullet_text:
# #         for key, value in request.GET.items():
# #             if key.startswith('bullet_') and value:
# #                 bullet_text = value
# #                 break
# #
# #     if not bullet_text:
# #         return HttpResponse("No bullet text found to enhance", status=400)
# #
# #     # Start timing for API response
# #     start_time = time.time()
# #
# #     # Choose AI engine based on user selection
# #     if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
# #         enhanced_text, input_tokens, output_tokens = enhance_bullet_chatgpt(
# #             bullet_text,
# #             enhancement_type,
# #             job_description
# #         )
# #     elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
# #         enhanced_text, input_tokens, output_tokens = enhance_bullet_gemini(
# #             bullet_text,
# #             enhancement_type,
# #             job_description
# #         )
# #     else:
# #         # Fallback to basic enhancement
# #         enhanced_text = enhance_bullet_basic(bullet_text)
# #         input_tokens = output_tokens = 0
# #
# #     # Calculate API response time
# #     response_time = time.time() - start_time
# #
# #     # Log API usage if using AI
# #     if (ai_engine == 'chatgpt' and settings.OPENAI_API_KEY) or (
# #             ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY):
# #         try:
# #             # Create API usage record
# #             usage = APIUsage(
# #                 user=request.user,
# #                 api_name=ai_engine,
# #                 operation='content_enhancement',
# #                 input_tokens=input_tokens,
# #                 output_tokens=output_tokens,
# #                 response_time=response_time,
# #                 status='success'
# #             )
# #             usage.calculate_cost()
# #             usage.save()
# #         except Exception as e:
# #             print(f"Error logging API usage: {str(e)}")
# #
# #     # Return the enhanced text
# #     return HttpResponse(enhanced_text)
# #
# #
# #
# #
# # @login_required
# # @require_http_methods(["GET"])
# # def ats_optimize_bullet(request):
# #     """
# #     Optimize a bullet point for ATS systems using AI.
# #     This is an HTMX endpoint that returns the optimized text.
# #     """
# #     bullet_text = request.GET.get('bullet_text', '')
# #     job_description = request.GET.get('job_description', '')
# #     ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Default to ChatGPT
# #
# #     # Try to get bullet text from form
# #     if not bullet_text:
# #         for key, value in request.GET.items():
# #             if key.startswith('bullet_') and value:
# #                 bullet_text = value
# #                 break
# #
# #     if not bullet_text:
# #         return HttpResponse("No bullet text provided", status=400)
# #
# #     # If job description not provided, try to get from active job target
# #     if not job_description:
# #         # Look for recent job inputs from this user
# #         try:
# #             job_input = JobInput.objects.filter(user=request.user).order_by('-created_at').first()
# #             if job_input:
# #                 job_description = job_input.job_description
# #         except:
# #             pass  # Continue without job description
# #
# #     # Start timing for API response
# #     start_time = time.time()
# #
# #     # Choose AI engine based on user selection
# #     if ai_engine == 'chatgpt' and settings.OPENAI_API_KEY:
# #         optimized_text, input_tokens, output_tokens = ats_optimize_chatgpt(bullet_text, job_description)
# #     elif ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY:
# #         optimized_text, input_tokens, output_tokens = ats_optimize_gemini(bullet_text, job_description)
# #     else:
# #         # If no AI available, return original text
# #         return HttpResponse(bullet_text)
# #
# #     # Calculate API response time
# #     response_time = time.time() - start_time
# #
# #     # Log API usage
# #     if (ai_engine == 'chatgpt' and settings.OPENAI_API_KEY) or (
# #             ai_engine == 'gemini' and settings.GOOGLE_GENAI_API_KEY):
# #         try:
# #             # Create API usage record
# #             usage = APIUsage(
# #                 user=request.user,
# #                 api_name=ai_engine,
# #                 operation='content_generation',
# #                 input_tokens=input_tokens,
# #                 output_tokens=output_tokens,
# #                 response_time=response_time,
# #                 status='success'
# #             )
# #             usage.calculate_cost()
# #             usage.save()
# #         except Exception as e:
# #             print(f"Error logging API usage: {str(e)}")
# #
# #     # Return the optimized text
# #     return HttpResponse(optimized_text)
# #
# #
# # @login_required
# # def check_bullet_strength(request):
# #     """
# #     Evaluate the strength of a bullet point and provide feedback.
# #     This is an HTMX endpoint that returns HTML for the feedback.
# #     """
# #     bullet_text = request.GET.get('bullet_text', '')
# #
# #     if not bullet_text:
# #         return HttpResponse("")
# #
# #     # Analyze the bullet point
# #     score = 0
# #     feedback = []
# #
# #     # Check for action verbs at beginning
# #     action_verbs = ["Achieved", "Analyzed", "Built", "Coordinated", "Created", "Delivered",
# #                     "Designed", "Developed", "Established", "Generated", "Implemented",
# #                     "Improved", "Led", "Managed", "Optimized", "Reduced", "Spearheaded",
# #                     "Launched", "Executed", "Streamlined", "Transformed", "Increased",
# #                     "Directed", "Orchestrated", "Pioneered", "Restructured"]
# #
# #     starts_with_action = any(bullet_text.startswith(verb) for verb in action_verbs)
# #     if starts_with_action:
# #         score += 2
# #     else:
# #         feedback.append("Start with a strong action verb")
# #
# #     # Check for metrics/quantifiable results
# #     has_numbers = any(c.isdigit() for c in bullet_text)
# #     if has_numbers:
# #         score += 2
# #         # Check for percentage or dollar amounts
# #         if '%' in bullet_text or '$' in bullet_text:
# #             score += 1
# #     else:
# #         feedback.append("Add measurable results (numbers, %, $)")
# #
# #     # Check length
# #     if 80 <= len(bullet_text) <= 150:
# #         score += 2
# #     elif len(bullet_text) < 80:
# #         feedback.append("Too brief - expand with more details")
# #         score += 0
# #     else:
# #         feedback.append("Too lengthy - try to be more concise")
# #         score += 0
# #
# #     # Generate rating based on score
# #     if score >= 5:
# #         rating = "Excellent! ★★★★★"
# #         color = "text-success"
# #     elif score >= 3:
# #         rating = "Good ★★★★☆"
# #         color = "text-success"
# #     elif score >= 2:
# #         rating = "Average ★★★☆☆"
# #         color = "text-warning"
# #     else:
# #         rating = "Needs improvement ★★☆☆☆"
# #         color = "text-error"
# #
# #     # Construct feedback HTML
# #     result = f'<span class="{color}">{rating}</span>'
# #
# #     if feedback:
# #         result += f' <span class="text-xs text-gray-500">Tip: {feedback[0]}</span>'
# #
# #     return HttpResponse(result)