# File: services/bullets_ai_services.py
# services/bullets_ai_services.py

import time
import logging
import json
import openai
import google.generativeai as genai
from django.conf import settings
from services.prompts.experience_prompts import (
    get_dynamic_bullet_generation_prompt,
    BULLET_ENHANCEMENT_PROMPT,
    ATS_OPTIMIZATION_PROMPT,
    RESUME_WRITER_SYSTEM_MESSAGE,
    ATS_EXPERT_SYSTEM_MESSAGE
)

logger = logging.getLogger(__name__)


class AIClientManager:
    """
    Manages AI client initialization with user-provided API keys
    """

    @staticmethod
    def get_openai_client(user_api_key=None):
        """Initialize and return OpenAI client with user's API key or fallback to settings"""
        api_key = user_api_key or getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            logger.warning("No OpenAI API key available")
            return None

        try:
            return openai.OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return None

    @staticmethod
    def get_gemini_client(user_api_key=None):
        """Initialize and return Gemini client with user's API key or fallback to settings"""
        api_key = user_api_key or getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
        if not api_key:
            logger.warning("No Gemini API key available")
            return None

        try:
            genai.configure(api_key=api_key)
            model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-pro')
            return genai.GenerativeModel(model_name)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            return None


# Experience Bullet Point Generation
def generate_bullets_chatgpt(
        job_title,
        employer=None,
        target_job_title=None,
        skills=None,
        responsibilities=None,
        num_bullets=3,
        user_api_key=None
):
    """
    Generate bullet points for a resume job experience using ChatGPT.
    Employer is optional, API key can be provided by user.
    """
    start_time = time.time()
    openai_client = AIClientManager.get_openai_client(user_api_key)

    if not openai_client:
        logger.error("OpenAI client could not be initialized for bullet generation")
        return ["Error: OpenAI API key not configured or invalid."], 0, 0

    try:
        # Create dynamic prompt
        prompt = get_dynamic_bullet_generation_prompt(
            job_title=job_title,
            employer=employer,
            target_job_title=target_job_title,
            skills=skills,
            responsibilities=responsibilities,
            bullet_count=num_bullets
        )

        # Request to ChatGPT
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        # Process response
        response_text = response.choices[0].message.content.strip()
        bullets = [line.strip() for line in response_text.split('\n') if line.strip()]

        # Limit bullets to requested number
        bullets = bullets[:num_bullets]

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        logger.info(f"Generated {len(bullets)} bullet points using ChatGPT in {time.time() - start_time:.2f}s")
        return bullets, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"Error generating bullets with ChatGPT: {str(e)}")
        error_msg = f"Error generating bullets: {str(e)[:100]}..."
        return [error_msg], 0, 0


def generate_bullets_gemini(
        job_title,
        employer=None,
        target_job_title=None,
        skills=None,
        responsibilities=None,
        num_bullets=3,
        user_api_key=None
):
    """
    Generate bullet points for a resume job experience using Google's Gemini.
    Employer is optional, API key can be provided by user.
    """
    start_time = time.time()
    gemini_client = AIClientManager.get_gemini_client(user_api_key)

    if not gemini_client:
        logger.error("Gemini client could not be initialized for bullet generation")
        return ["Error: Gemini API key not configured or invalid."], 0, 0

    try:
        # Create dynamic prompt
        prompt = get_dynamic_bullet_generation_prompt(
            job_title=job_title,
            employer=employer,
            target_job_title=target_job_title,
            skills=skills,
            responsibilities=responsibilities,
            bullet_count=num_bullets
        )

        # Request to Gemini
        response = gemini_client.generate_content(prompt)
        response_text = response.text.strip()

        # Process response
        bullets = [line.strip() for line in response_text.split('\n') if line.strip()]

        # Limit bullets to requested number
        bullets = bullets[:num_bullets]

        # Estimate token count (Gemini doesn't provide token counts directly)
        input_chars = len(prompt)
        output_chars = len(response_text)
        input_tokens = input_chars // 4  # Rough estimate: 1 token ≈ 4 characters
        output_tokens = output_chars // 4

        logger.info(f"Generated {len(bullets)} bullet points using Gemini in {time.time() - start_time:.2f}s")
        return bullets, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"Error generating bullets with Gemini: {str(e)}")
        error_msg = f"Error generating bullets: {str(e)[:100]}..."
        return [error_msg], 0, 0


# Template-based fallback
def get_template_bullets(job_title, employer=None, num_bullets=3):
    """
    Return template-based bullet points if AI generation fails.
    Employer is optional.
    """
    template_bullets = {
        "software engineer": [
            "Developed scalable web applications using React and Node.js, improving user experience and performance by 30%",
            "Collaborated with cross-functional teams to implement new features and optimize existing functionality",
            "Conducted code reviews and implemented best practices, reducing bugs by 25% and improving code quality",
            "Architected and deployed microservices using Docker and Kubernetes, increasing system reliability and scalability"
        ],
        "product manager": [
            "Led cross-functional teams to successfully launch 3 major product features, increasing user engagement by 40%",
            "Analyzed customer feedback and usage data to identify opportunities for product improvements and optimization",
            "Created and maintained product roadmaps, aligning stakeholder expectations with technical feasibility",
            "Conducted market research to identify competitive advantages, resulting in 20% increase in conversion rates"
        ],
        "data scientist": [
            "Developed predictive models that improved accuracy by 35% and reduced processing time by 40%",
            "Extracted actionable insights from large datasets using SQL, Python, and advanced statistical methods",
            "Created interactive dashboards in Tableau to visualize key metrics for executive stakeholders",
            "Implemented machine learning algorithms that automated manual processes, saving 20 hours weekly"
        ],
        "marketing specialist": [
            "Executed digital marketing campaigns across multiple channels, generating 45% increase in lead conversion",
            "Analyzed marketing performance metrics to optimize campaign strategies and improve ROI by 30%",
            "Created compelling content for social media platforms, increasing engagement by 50%",
            "Collaborated with design team to develop brand-aligned marketing materials for product launches"
        ],
        "project manager": [
            "Managed cross-functional teams of 8-12 members to deliver projects on time and within budget constraints",
            "Developed comprehensive project plans and monitored progress, identifying and resolving bottlenecks",
            "Facilitated stakeholder meetings to align expectations and communicate project status effectively",
            "Implemented agile methodologies that improved team efficiency by 35% and reduced delivery timeframes"
        ]
    }

    # Normalize job title to check against dictionary
    normalized_title = job_title.lower()

    # Find the closest match or use generic bullets
    job_key = next((key for key in template_bullets.keys() if key in normalized_title), "generic")

    if job_key == "generic":
        # Generic bullets that can work for most jobs
        generic_bullets = [
            f"Exceeded performance targets consistently while working as a {job_title}",
            f"Collaborated effectively with team members and stakeholders to achieve organizational goals",
            f"Implemented process improvements that enhanced efficiency and productivity",
            f"Developed innovative solutions to complex problems, saving time and resources"
        ]
        bullets = generic_bullets
    else:
        bullets = template_bullets[job_key]

    # Customize with employer if provided
    if employer:
        bullets = [b.replace("working as a", f"at {employer} as a") for b in bullets]

    # Return requested number of bullets
    return bullets[:num_bullets]


# Bullet Enhancement
def enhance_bullet_chatgpt(bullet_text, enhancement_type='general', job_description='', user_api_key=None):
    """
    Enhance a bullet point using ChatGPT.
    Enhancement types: 'general', 'ats', 'metrics', 'leadership', 'technical'
    """
    start_time = time.time()
    openai_client = AIClientManager.get_openai_client(user_api_key)

    if not openai_client:
        logger.error("OpenAI client could not be initialized for bullet enhancement")
        return bullet_text, 0, 0

    try:
        if enhancement_type == 'ats' and job_description:
            # Include job description for ATS optimization
            job_description_section = f"Job Description Context: {job_description[:500]}..."
            prompt = ATS_OPTIMIZATION_PROMPT.format(
                bullet_text=bullet_text,
                job_description_section=job_description_section
            )
            system_msg = ATS_EXPERT_SYSTEM_MESSAGE
        else:
            # General enhancement
            prompt = BULLET_ENHANCEMENT_PROMPT.format(bullet_text=bullet_text)
            system_msg = RESUME_WRITER_SYSTEM_MESSAGE

        # Request to ChatGPT
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.6
        )

        # Process response
        enhanced_text = response.choices[0].message.content.strip()
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        logger.info(f"Enhanced bullet with ChatGPT in {time.time() - start_time:.2f}s")
        return enhanced_text, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"Error enhancing bullet with ChatGPT: {str(e)}")
        return bullet_text, 0, 0


def enhance_bullet_gemini(bullet_text, enhancement_type='general', job_description='', user_api_key=None):
    """
    Enhance a bullet point using Google's Gemini.
    Enhancement types: 'general', 'ats', 'metrics', 'leadership', 'technical'
    """
    start_time = time.time()
    gemini_client = AIClientManager.get_gemini_client(user_api_key)

    if not gemini_client:
        logger.error("Gemini client could not be initialized for bullet enhancement")
        return bullet_text, 0, 0

    try:
        if enhancement_type == 'ats' and job_description:
            # Include job description for ATS optimization
            job_description_section = f"Job Description Context: {job_description[:500]}..."
            prompt = ATS_OPTIMIZATION_PROMPT.format(
                bullet_text=bullet_text,
                job_description_section=job_description_section
            )
        else:
            # General enhancement
            prompt = BULLET_ENHANCEMENT_PROMPT.format(bullet_text=bullet_text)

        # Request to Gemini
        response = gemini_client.generate_content(prompt)
        enhanced_text = response.text.strip()

        # Estimate token count
        input_chars = len(prompt)
        output_chars = len(enhanced_text)
        input_tokens = input_chars // 4
        output_tokens = output_chars // 4

        logger.info(f"Enhanced bullet with Gemini in {time.time() - start_time:.2f}s")
        return enhanced_text, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"Error enhancing bullet with Gemini: {str(e)}")
        return bullet_text, 0, 0


def enhance_bullet_basic(bullet_text):
    """
    Simple rule-based enhancement for bullet points when AI is unavailable.
    """
    try:
        enhanced = bullet_text.strip()

        # Ensure starts with action verb
        common_action_verbs = [
            "Achieved", "Analyzed", "Built", "Created", "Delivered", "Developed",
            "Established", "Generated", "Implemented", "Improved", "Increased",
            "Led", "Managed", "Optimized", "Reduced", "Streamlined"
        ]

        # Check if bullet starts with an action verb
        first_word = enhanced.split(' ')[0].rstrip(',;:.')
        if first_word.lower() not in [verb.lower() for verb in common_action_verbs]:
            # Add a generic action verb if none is present
            enhanced = f"Delivered {enhanced[0].lower()}{enhanced[1:]}"

        # Ensure first letter is capitalized
        if enhanced and not enhanced[0].isupper():
            enhanced = f"{enhanced[0].upper()}{enhanced[1:]}"

        # Add period at the end if missing
        if enhanced and not enhanced.endswith(('.', '!', '?')):
            enhanced = f"{enhanced}."

        return enhanced

    except Exception as e:
        logger.error(f"Error in basic bullet enhancement: {str(e)}")
        return bullet_text


def ats_optimize_chatgpt(bullet_text, job_description, user_api_key=None):
    """Optimize a bullet point for ATS using ChatGPT."""
    return enhance_bullet_chatgpt(bullet_text, 'ats', job_description, user_api_key)


def ats_optimize_gemini(bullet_text, job_description, user_api_key=None):
    """Optimize a bullet point for ATS using Gemini."""
    return enhance_bullet_gemini(bullet_text, 'ats', job_description, user_api_key)

# import openai
# import google.generativeai as genai
# import json
# import logging
# from django.conf import settings  # Still needed for settings.OPENAI_MODEL
# # Corrected import for experience_prompts
# from services.prompts import experience_prompts
#
# # Initialize logger
# logger = logging.getLogger(__name__)
#
#
# class APIClient:
#     def __init__(self, user_openai_key=None, user_gemini_key=None):
#         # API keys are now strictly from user input
#         self.user_openai_key = user_openai_key
#         self.user_gemini_key = user_gemini_key
#
#         self.openai_client = self._get_openai_client()
#         self.gemini_client = self._get_gemini_client()
#
#     def _get_openai_client(self):
#         if not self.user_openai_key:
#             logger.warning("OpenAI API key was not provided by the user.")
#             return None
#         try:
#             return openai.OpenAI(api_key=self.user_openai_key)
#         except Exception as e:
#             logger.error(f"Failed to initialize OpenAI client with user-provided key: {e}")
#             return None
#
#     def _get_gemini_client(self):
#         if not self.user_gemini_key:
#             logger.warning("Gemini API key was not provided by the user.")
#             return None
#         try:
#             genai.configure(api_key=self.user_gemini_key)
#             # Ensure you are using a model that supports the generate_content method as used.
#             # 'gemini-pro' is a common choice for text generation.
#             return genai.GenerativeModel(
#                 settings.GEMINI_MODEL_NAME if hasattr(settings, 'GEMINI_MODEL_NAME') else 'gemini-pro')
#         except Exception as e:
#             logger.error(f"Failed to initialize Gemini client with user-provided key: {e}")
#             return None
#
#     def generate_bullet_points_from_ai(self, job_title, company, description, skills, tone, count=3,
#                                        ai_provider="gemini"):
#         if ai_provider == "openai" and not self.openai_client:
#             return {"error": "OpenAI client not initialized. Please provide your OpenAI API key."}
#         if ai_provider == "gemini" and not self.gemini_client:
#             return {"error": "Gemini client not initialized. Please provide your Gemini API key."}
#
#         try:
#             context_prompt = experience_prompts.JOB_DESCRIPTION_PARSER_PROMPT.format(
#                 job_title=job_title,
#                 company_name=company,
#                 job_description=description,
#                 skills=skills,
#                 tone=tone,
#                 bullet_point_count=count
#             )
#
#             final_prompt = experience_prompts.GENERATE_BULLET_POINTS_PROMPT.format(
#                 original_description=context_prompt,
#                 job_title=job_title,
#                 company=company,
#                 skills=", ".join(skills) if isinstance(skills, list) else skills,
#                 tone=tone,
#                 count=count
#             )
#
#             logger.debug(f"Generating bullet points with {ai_provider}. User-provided key used.")
#
#             if ai_provider == "openai":
#                 response = self.openai_client.chat.completions.create(
#                     model=settings.OPENAI_MODEL,
#                     messages=[{"role": "user", "content": final_prompt}]
#                 )
#                 content = response.choices[0].message.content
#                 return json.loads(content)
#             elif ai_provider == "gemini":
#                 response = self.gemini_client.generate_content(final_prompt)
#                 return json.loads(response.text)
#             else:
#                 return {"error": "AI provider not supported."}
#
#         except json.JSONDecodeError as e:
#             logger.error(f"JSONDecodeError in generate_bullet_points_from_ai ({ai_provider}): {e}")
#             raw_response = "Unavailable"
#             if 'response' in locals():
#                 if ai_provider == "openai" and hasattr(response, 'choices') and response.choices:
#                     raw_response = response.choices[0].message.content
#                 elif ai_provider == "gemini" and hasattr(response, 'text'):
#                     raw_response = response.text
#             logger.error(f"Raw response from {ai_provider} was: {raw_response}")
#             return {"error": f"Failed to decode AI response. Raw response: {raw_response}"}
#         except Exception as e:
#             logger.error(f"Error processing with {ai_provider} in generate_bullet_points_from_ai: {e}")
#             return {"error": f"An error occurred with {ai_provider}: {str(e)}"}
#
#     def enhance_bullet_points_from_ai(self, job_title, company, description, bullet_points, tone, ai_provider="gemini"):
#         if ai_provider == "openai" and not self.openai_client:
#             return {"error": "OpenAI client not initialized. Please provide your OpenAI API key."}
#         if ai_provider == "gemini" and not self.gemini_client:
#             return {"error": "Gemini client not initialized. Please provide your Gemini API key."}
#
#         try:
#             if isinstance(bullet_points, list):
#                 bullet_points_str = "\n".join(bullet_points)
#             else:
#                 bullet_points_str = bullet_points
#
#             final_prompt = experience_prompts.ENHANCE_BULLET_POINTS_PROMPT.format(
#                 job_title=job_title,
#                 company_name=company,
#                 job_description=description,
#                 bullet_points=bullet_points_str,
#                 tone=tone
#             )
#             logger.debug(f"Enhancing bullet points with {ai_provider}. User-provided key used.")
#
#             if ai_provider == "openai":
#                 response = self.openai_client.chat.completions.create(
#                     model=settings.OPENAI_MODEL,
#                     messages=[{"role": "user", "content": final_prompt}]
#                 )
#                 content = response.choices[0].message.content
#                 return json.loads(content)
#             elif ai_provider == "gemini":
#                 response = self.gemini_client.generate_content(final_prompt)
#                 return json.loads(response.text)
#             else:
#                 return {"error": "AI provider not supported."}
#
#         except json.JSONDecodeError as e:
#             logger.error(f"JSONDecodeError in enhance_bullet_points_from_ai ({ai_provider}): {e}")
#             raw_response = "Unavailable"
#             if 'response' in locals():
#                 if ai_provider == "openai" and hasattr(response, 'choices') and response.choices:
#                     raw_response = response.choices[0].message.content
#                 elif ai_provider == "gemini" and hasattr(response, 'text'):
#                     raw_response = response.text
#             logger.error(f"Raw response from {ai_provider} was: {raw_response}")
#             return {"error": f"Failed to decode AI response. Raw response: {raw_response}"}
#         except Exception as e:
#             logger.error(f"Error processing with {ai_provider} in enhance_bullet_points_from_ai: {e}")
#             return {"error": f"An error occurred with {ai_provider}: {str(e)}"}

# # services/bullets_ai_services.py
# import time
# import random
# from openai import OpenAI, APIError as OpenAIAPIError  # MODIFIED: New import for client and specific errors
# import google.generativeai as genai
# from django.conf import settings
# import logging
#
# from services.prompts.experience_prompts import get_dynamic_bullet_generation_prompt, RESUME_WRITER_SYSTEM_MESSAGE, \
#     BULLET_ENHANCEMENT_PROMPT, ATS_OPTIMIZATION_PROMPT, ATS_EXPERT_SYSTEM_MESSAGE
#
# # Import the dynamic prompt generation function and other necessary prompts/messages
#
#
# logger = logging.getLogger(__name__)
#
# # Initialize OpenAI client (new SDK v1.x.x)
# openai_client = None
# if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
#     try:
#         openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
#         logger.info("OpenAI client initialized with new SDK.")
#     except Exception as e:
#         logger.error(f"Failed to initialize OpenAI client with new SDK: {e}", exc_info=True)
# else:
#     logger.info("OpenAI API key is not configured in settings or is empty. OpenAI client not initialized.")
#
# # Initialize Google GenAI (Gemini)
# try:
#     if hasattr(settings, 'GOOGLE_GENAI_API_KEY') and settings.GOOGLE_GENAI_API_KEY:
#         genai.configure(api_key=settings.GOOGLE_GENAI_API_KEY)
#         logger.info("Google GenAI (Gemini) API configured.")
#     else:
#         logger.info("Google GenAI (Gemini) API key is not configured in settings or is empty.")
# except AttributeError:
#     logger.info("GOOGLE_GENAI_API_KEY attribute not found in settings.")
# except Exception as e:
#     logger.error(f"Error configuring Google GenAI (Gemini): {e}", exc_info=True)
#
#
# # Generate bullet points using ChatGPT (OpenAI SDK v1.x.x)
# def generate_bullets_chatgpt(job_title, employer=None, target_job_title=None, skills=None, responsibilities=None,
#                              num_bullets=3):
#     if not openai_client:  # Check if client was initialized
#         logger.warning("OpenAI client not initialized. Cannot generate bullets with ChatGPT.")
#         # Return a list of error messages, one for each expected bullet
#         return ["OpenAI API key not configured or client failed to initialize. Please check settings."] * num_bullets, 0, 0
#
#     prompt_text = get_dynamic_bullet_generation_prompt(
#         job_title, employer, target_job_title, skills, responsibilities, num_bullets
#     )
#     input_tokens = 0
#     output_tokens = 0
#
#     try:
#         start_time = time.time()
#         # Ensure settings.OPENAI_MODEL_NAME_CHATCOMPLETION is defined in your settings.py
#         model_name = getattr(settings, 'OPENAI_MODEL_NAME_CHATCOMPLETION', 'gpt-3.5-turbo')  # Default if not set
#
#         # MODIFIED: New OpenAI SDK call structure
#         response = openai_client.chat.completions.create(
#             model=model_name,
#             messages=[
#                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
#                 {"role": "user", "content": prompt_text}
#             ],
#             max_tokens=350,  # Adjusted for potentially more comprehensive bullets
#             n=1,
#             stop=None,
#             temperature=0.6,  # Slightly lower for more factual resume bullets
#         )
#         end_time = time.time()
#         logger.info(f"ChatGPT API call for bullet generation took {end_time - start_time:.2f} seconds")
#
#         content = response.choices[0].message.content.strip() if response.choices and response.choices[
#             0].message else ""
#         bullets = [b.strip() for b in content.split('\n') if b.strip() and len(b.strip()) > 10]  # Basic filter
#
#         if not bullets:
#             logger.warning(
#                 f"ChatGPT returned empty or unparsable bullet response for: {job_title}. Raw content: '{content}'")
#             bullets = [f"Could not generate bullet for '{job_title}' (AI response was empty or invalid)."] * num_bullets
#
#         # Ensure the correct number of bullets
#         final_bullets = bullets[:num_bullets]
#         while len(final_bullets) < num_bullets:
#             final_bullets.append("Placeholder: Additional bullet could not be generated by AI.")
#
#         if response.usage:  # MODIFIED: Accessing usage information
#             input_tokens = response.usage.prompt_tokens
#             output_tokens = response.usage.completion_tokens
#
#         return final_bullets, input_tokens, output_tokens
#
#     except OpenAIAPIError as e:  # MODIFIED: Specific error handling for new SDK
#         logger.error(
#             f"OpenAI API error during bullet generation: Status {e.status_code}, Type: {e.type}, Message: {e.message}",
#             exc_info=True)
#         error_message = f"Error (OpenAI: {e.status_code} - {e.type if e.type else 'APIError'}). Please check API key/quota and try again."
#         return [error_message] * num_bullets, 0, 0
#     except Exception as e:
#         logger.error(f"Unexpected error in generate_bullets_chatgpt: {e}", exc_info=True)
#         return [f"Unexpected server error during bullet generation. Please check logs."] * num_bullets, 0, 0
#
#
# # Generate bullet points using Gemini
# def generate_bullets_gemini(job_title, employer=None, target_job_title=None, skills=None, responsibilities=None,
#                             num_bullets=3):
#     if not (hasattr(settings, 'GOOGLE_GENAI_API_KEY') and settings.GOOGLE_GENAI_API_KEY):
#         logger.warning("Google Gemini API key not configured. Cannot generate bullets with Gemini.")
#         return ["Google Gemini API key not configured. Please add it to your settings."] * num_bullets, 0, 0
#
#     prompt_text = get_dynamic_bullet_generation_prompt(
#         job_title, employer, target_job_title, skills, responsibilities, num_bullets
#     )
#     input_tokens = 0
#     output_tokens = 0
#
#     try:
#         model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-pro')
#         model = genai.GenerativeModel(model_name)
#
#         start_time = time.time()
#         full_prompt = f"{RESUME_WRITER_SYSTEM_MESSAGE}\n\nUser Request:\n{prompt_text}"
#
#         response = model.generate_content(
#             full_prompt,
#             generation_config=genai.types.GenerationConfig(
#                 max_output_tokens=350,
#                 temperature=0.6
#             )
#         )
#         end_time = time.time()
#         logger.info(f"Gemini API call for bullet generation took {end_time - start_time:.2f} seconds")
#
#         generated_text = ""
#         # More robust check for Gemini response parts and safety
#         if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
#             generated_text = response.candidates[0].content.parts[0].text.strip()
#
#         if not generated_text:  # This covers blocked content or if parts[0].text is empty
#             block_reason_detail = "Content not generated or was empty."
#             if hasattr(response,
#                        'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
#                 block_reason = response.prompt_feedback.block_reason.name if hasattr(
#                     response.prompt_feedback.block_reason, 'name') else str(response.prompt_feedback.block_reason)
#                 safety_ratings_str = ", ".join([f"{s.category.name}: {s.probability.name}" for s in
#                                                 response.prompt_feedback.safety_ratings]) if response.prompt_feedback.safety_ratings else "N/A"
#                 block_reason_detail = f"Blocked by Gemini (Reason: {block_reason}). Safety: {safety_ratings_str}"
#             elif hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0],
#                                                                                      'finish_reason') and \
#                     response.candidates[0].finish_reason != 1:  # FINISH_REASON_STOP = 1
#                 finish_reason_name = response.candidates[0].finish_reason.name if hasattr(
#                     response.candidates[0].finish_reason, 'name') else str(response.candidates[0].finish_reason)
#                 block_reason_detail = f"Finished with reason: {finish_reason_name}"
#
#             logger.warning(f"Gemini content generation issue: {block_reason_detail}")
#             return [f"Gemini issue: {block_reason_detail}. Please rephrase input or check safety settings."] * num_bullets, 0, 0
#
#         bullets = [b.strip() for b in generated_text.split('\n') if b.strip() and len(b.strip()) > 10]
#
#         if not bullets:
#             logger.warning(
#                 f"Gemini returned empty or unparsable bullet response for: {job_title}. Raw content: '{generated_text}'")
#             bullets = [f"Could not generate bullet for '{job_title}' (Gemini response was empty or invalid)."] * num_bullets
#
#         final_bullets = bullets[:num_bullets]
#         while len(final_bullets) < num_bullets:
#             final_bullets.append("Placeholder: Additional bullet could not be generated by AI.")
#
#         return final_bullets, input_tokens, output_tokens
#
#     except Exception as e:
#         logger.error(f"Google GenAI (Gemini) API error during bullet generation: {e}", exc_info=True)
#         return [f"Error generating bullets (Gemini: {str(e)[:60]}...). Please try again."] * num_bullets, 0, 0
#
#
# # Template-based bullet points (fallback)
# def get_template_bullets(job_title, employer=None, num_bullets=3):
#     employer_phrase = f"at {employer.strip()}" if employer and employer.strip() else "in a previous role"
#     generic_bullets = [
#         f"Spearheaded key initiatives {employer_phrase} that improved operational efficiency by [Number]% and reduced annual costs by $[Amount].",
#         f"Collaborated with cross-functional teams {employer_phrase} to implement best practices and streamline workflows, increasing productivity by [Number]%.",
#         f"Managed multiple projects simultaneously {employer_phrase}, meeting 100% of deadlines while maintaining exceptional quality standards.",
#         f"Recognized for outstanding performance {employer_phrase}, receiving commendation from senior leadership for contributions to company growth.",
#         f"Applied strong analytical and technical skills to address complex challenges {employer_phrase}, leading to [Specific Positive Outcome]."
#     ]
#     random.shuffle(generic_bullets)
#     selected_bullets = generic_bullets[:num_bullets]
#     while len(selected_bullets) < num_bullets:
#         selected_bullets.append(
#             f"Effectively contributed to team success {employer_phrase} through consistent effort and dedication.")
#     return selected_bullets[:num_bullets]
#
#
# # --- Enhancement and ATS Optimization Functions (Updated for new OpenAI SDK) ---
#
# def enhance_bullet_chatgpt(bullet_text, enhancement_type='general', job_description=''):
#     if not openai_client:
#         logger.warning("OpenAI client not initialized for enhancement.")
#         return "OpenAI API key not configured or client failed to initialize.", 0, 0
#
#     prompt = BULLET_ENHANCEMENT_PROMPT.format(bullet_text=bullet_text)
#     if enhancement_type == 'ats' and job_description:  # Assuming 'ats' is a possible enhancement_type
#         prompt += f"\n\nConsider the following job description context for ATS alignment:\n{job_description}"
#
#     input_tokens = 0
#     output_tokens = 0
#     try:
#         model_name = getattr(settings, 'OPENAI_MODEL_NAME_CHATCOMPLETION', 'gpt-3.5-turbo')
#         response = openai_client.chat.completions.create(  # MODIFIED
#             model=model_name,
#             messages=[
#                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=150,
#             temperature=0.5,
#         )
#         enhanced_text = response.choices[0].message.content.strip() if response.choices and response.choices[
#             0].message else ""
#         if response.usage:
#             input_tokens = response.usage.prompt_tokens
#             output_tokens = response.usage.completion_tokens
#         return enhanced_text, input_tokens, output_tokens
#     except OpenAIAPIError as e:  # MODIFIED
#         logger.error(f"OpenAI API error during enhancement: Status {e.status_code}, Type: {e.type}", exc_info=True)
#         return f"Error enhancing bullet (OpenAI: {e.status_code} - {e.type if e.type else 'APIError'}).", 0, 0
#     except Exception as e:
#         logger.error(f"Unexpected error in enhance_bullet_chatgpt: {e}", exc_info=True)
#         return f"Unexpected error during enhancement.", 0, 0
#
#
# def enhance_bullet_gemini(bullet_text, enhancement_type='general', job_description=''):
#     if not (hasattr(settings, 'GOOGLE_GENAI_API_KEY') and settings.GOOGLE_GENAI_API_KEY):
#         logger.warning("Google Gemini API key not configured for enhancement.")
#         return "Google Gemini API key not configured.", 0, 0
#
#     prompt = BULLET_ENHANCEMENT_PROMPT.format(bullet_text=bullet_text)
#     if enhancement_type == 'ats' and job_description:
#         prompt += f"\n\nConsider the following job description context for ATS alignment:\n{job_description}"
#
#     input_tokens = 0
#     output_tokens = 0
#     try:
#         model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-pro')
#         model = genai.GenerativeModel(model_name)
#         full_prompt = f"{RESUME_WRITER_SYSTEM_MESSAGE}\n\nUser Request:\n{prompt}"
#         response = model.generate_content(
#             full_prompt,
#             generation_config=genai.types.GenerationConfig(
#                 max_output_tokens=150,
#                 temperature=0.5
#             )
#         )
#         generated_text = ""
#         if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
#             generated_text = response.candidates[0].content.parts[0].text.strip()
#
#         if not generated_text:
#             block_reason_detail = "Content not generated or was empty."
#             # ... (same detailed block reason logging as in generate_bullets_gemini)
#             if hasattr(response,
#                        'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
#                 block_reason = response.prompt_feedback.block_reason.name if hasattr(
#                     response.prompt_feedback.block_reason, 'name') else str(response.prompt_feedback.block_reason)
#                 block_reason_detail = f"Blocked by Gemini (Reason: {block_reason})."
#             elif hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0],
#                                                                                      'finish_reason') and \
#                     response.candidates[0].finish_reason != 1:
#                 finish_reason_name = response.candidates[0].finish_reason.name if hasattr(
#                     response.candidates[0].finish_reason, 'name') else str(response.candidates[0].finish_reason)
#                 block_reason_detail = f"Finished with reason: {finish_reason_name}"
#             logger.warning(f"Gemini content enhancement issue: {block_reason_detail}")
#             return f"Gemini issue: {block_reason_detail}", 0, 0
#
#         return generated_text, input_tokens, output_tokens
#     except Exception as e:
#         logger.error(f"Google GenAI (Gemini) API error during enhancement: {e}", exc_info=True)
#         return f"Error enhancing bullet (Gemini: {str(e)[:60]}...).", 0, 0
#
#
# def enhance_bullet_basic(bullet_text):
#     return "Consider rephrasing with a strong action verb and adding quantifiable achievements: " + bullet_text
#
#
# def ats_optimize_chatgpt(bullet_text, job_description='', job_title=''):
#     if not openai_client:
#         logger.warning("OpenAI client not initialized for ATS optimization.")
#         return "OpenAI API key not configured or client failed to initialize.", 0, 0
#
#     job_desc_section = f"Relevant job description context (if any):\n{job_description}\n" if job_description else ""
#     # Ensure your ATS_OPTIMIZATION_PROMPT can handle job_title for context if job_description is empty
#     prompt = ATS_OPTIMIZATION_PROMPT.format(
#         bullet_text=bullet_text,
#         job_description_section=job_desc_section,
#         job_title=job_title  # Pass job_title for context in prompt
#     )
#     input_tokens = 0
#     output_tokens = 0
#     try:
#         model_name = getattr(settings, 'OPENAI_MODEL_NAME_CHATCOMPLETION', 'gpt-3.5-turbo')
#         response = openai_client.chat.completions.create(  # MODIFIED
#             model=model_name,
#             messages=[
#                 {"role": "system", "content": ATS_EXPERT_SYSTEM_MESSAGE},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=150,
#             temperature=0.5,
#         )
#         optimized_text = response.choices[0].message.content.strip() if response.choices and response.choices[
#             0].message else ""
#         if response.usage:
#             input_tokens = response.usage.prompt_tokens
#             output_tokens = response.usage.completion_tokens
#         return optimized_text, input_tokens, output_tokens
#     except OpenAIAPIError as e:  # MODIFIED
#         logger.error(f"OpenAI API error during ATS optimization: Status {e.status_code}, Type: {e.type}", exc_info=True)
#         return f"Error optimizing bullet (OpenAI: {e.status_code} - {e.type if e.type else 'APIError'}).", 0, 0
#     except Exception as e:
#         logger.error(f"Unexpected error in ats_optimize_chatgpt: {e}", exc_info=True)
#         return f"Unexpected error during ATS optimization.", 0, 0
#
#
# def ats_optimize_gemini(bullet_text, job_description='', job_title=''):
#     if not (hasattr(settings, 'GOOGLE_GENAI_API_KEY') and settings.GOOGLE_GENAI_API_KEY):
#         logger.warning("Google Gemini API key not configured for ATS optimization.")
#         return "Google Gemini API key not configured.", 0, 0
#
#     job_desc_section = f"Relevant job description context (if any):\n{job_description}\n" if job_description else ""
#     prompt = ATS_OPTIMIZATION_PROMPT.format(
#         bullet_text=bullet_text,
#         job_description_section=job_desc_section,
#         job_title=job_title
#     )
#     input_tokens = 0
#     output_tokens = 0
#     try:
#         model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-pro')
#         model = genai.GenerativeModel(model_name)
#         full_prompt = f"{ATS_EXPERT_SYSTEM_MESSAGE}\n\nUser Request:\n{prompt}"
#         response = model.generate_content(
#             full_prompt,
#             generation_config=genai.types.GenerationConfig(
#                 max_output_tokens=150,
#                 temperature=0.5
#             )
#         )
#         generated_text = ""
#         if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
#             generated_text = response.candidates[0].content.parts[0].text.strip()
#
#         if not generated_text:
#             block_reason_detail = "Content not generated or was empty."
#             # ... (same detailed block reason logging as in generate_bullets_gemini)
#             if hasattr(response,
#                        'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
#                 block_reason = response.prompt_feedback.block_reason.name if hasattr(
#                     response.prompt_feedback.block_reason, 'name') else str(response.prompt_feedback.block_reason)
#                 block_reason_detail = f"Blocked by Gemini (Reason: {block_reason})."
#             elif hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0],
#                                                                                      'finish_reason') and \
#                     response.candidates[0].finish_reason != 1:
#                 finish_reason_name = response.candidates[0].finish_reason.name if hasattr(
#                     response.candidates[0].finish_reason, 'name') else str(response.candidates[0].finish_reason)
#                 block_reason_detail = f"Finished with reason: {finish_reason_name}"
#             logger.warning(f"Gemini content ATS optimization issue: {block_reason_detail}")
#             return f"Gemini issue: {block_reason_detail}", 0, 0
#
#         return generated_text, input_tokens, output_tokens
#     except Exception as e:
#         logger.error(f"Google GenAI (Gemini) API error during ATS optimization: {e}", exc_info=True)
#         return f"Error optimizing bullet (Gemini: {str(e)[:60]}...).", 0, 0
#
# # # ai_services.py
# # import time
# # import random
# # import openai
#
#
# # import google.generativeai as genai
# # from django.conf import settings
# #
# # # Initialize APIs if keys are available
# # openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
# # genai_api_key = getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
# # if genai_api_key:
# #     genai.configure(api_key=genai_api_key)
# #
# # # Updated prompts with more ATS focus
# # RESUME_WRITER_SYSTEM_MESSAGE = """You are an expert resume writer specializing in ATS-optimized resumes.
# # Your task is to create impactful bullet points that highlight achievements, incorporate relevant skills,
# # and use industry-specific keywords that will pass through Applicant Tracking Systems."""
# #
# #
# # # Enhanced prompt for bullet generation with more parameters and configurable bullet count
# # def get_bullet_generation_prompt(job_title, employer, target_job_title, skills, responsibilities=None, bullet_count=3):
# #     """
# #     Get prompt for generating bullet points with configurable count.
# #     """
# #     # Ensure bullet_count is between 1 and 5
# #     bullet_count = min(max(int(bullet_count), 1), 5)
# #
# #     prompt = f"""Generate {bullet_count} professional resume bullet points for a {job_title} position at {employer}
# # that would be highly effective for applying to a {target_job_title} position.
# #
# # Incorporate these skills where relevant: {skills}
# #
# # """
# #
# #     if responsibilities:
# #         prompt += f"""
# # Based on these responsibilities/achievements: {responsibilities}
# # """
# #
# #     prompt += f"""
# # Each bullet point should:
# # 1. Start with a strong action verb
# # 2. Include measurable achievements with specific numbers (%, $, etc.)
# # 3. Be concise (100-150 characters optimal)
# # 4. Focus on accomplishments rather than just responsibilities
# # 5. Include keywords relevant to the target position
# # 6. Be optimized for Applicant Tracking Systems (ATS)
# #
# # Format the response as a simple list with one bullet point per line.
# # Provide exactly {bullet_count} bullet points.
# # Do not include bullet markers, numbers, or any other formatting."""
# #
# #     return prompt
# #
# #
# # # Enhanced bullet enhancement prompt
# # def get_bullet_enhancement_prompt(bullet_text, enhancement_type="general"):
# #     if enhancement_type == "ats":
# #         return f"""Optimize the following resume bullet point specifically for Applicant Tracking Systems (ATS):
# #
# # Original: {bullet_text}
# #
# # Instructions:
# # 1. Ensure it includes industry-standard keywords that ATS systems typically scan for
# # 2. Keep a strong action verb at the beginning
# # 3. Maintain quantifiable achievements and metrics
# # 4. Ensure it remains clear and readable for humans
# # 5. Keep it concise yet impactful (100-150 characters optimal)
# # 6. Do not add any fictional achievements or details
# #
# # Provide only the optimized bullet point text with no additional commentary."""
# #
# #     else:  # general enhancement
# #         return f"""Enhance the following resume bullet point to be more impactful:
# #
# # Original: {bullet_text}
# #
# # Instructions:
# # 1. Ensure it starts with a strong action verb
# # 2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
# # 3. Focus on achievements rather than responsibilities
# # 4. Keep it concise yet impactful (100-150 characters optimal)
# # 5. Maintain professional language and clarity
# # 6. Do not add any fictional achievements or details
# #
# # Provide only the enhanced bullet point text with no additional commentary."""
# #
# #
# # # ATS optimization prompt with job description
# # def get_ats_optimization_prompt(bullet_text, job_description=''):
# #     prompt = f"""Optimize the following resume bullet point for Applicant Tracking Systems (ATS):
# #
# # Original bullet point: {bullet_text}
# #
# # """
# #
# #     if job_description:
# #         prompt += f"""Target Job Description:
# # {job_description}
# #
# # """
# #
# #     prompt += """Instructions:
# # 1. Include relevant keywords from the job description when available
# # 2. Keep the strong action verb at the beginning
# # 3. Maintain quantifiable achievements and metrics
# # 4. Ensure it remains clear and readable for humans
# # 5. Keep it concise yet impactful
# # 6. Do not add any fictional achievements or details
# #
# # Provide only the optimized bullet point text with no additional commentary."""
# #
# #     return prompt
# # def generate_bullets_chatgpt(job_title, employer, target_job_title=None, skills=None, responsibilities=None, bullet_count=3):
# #     """
# #     Generate bullet points using OpenAI's GPT models with enhanced parameters and customizable count.
# #     Returns the bullet points and token counts.
# #     """
# #     if not openai.api_key:
# #         return get_template_bullets(job_title, employer, bullet_count), 0, 0
# #
# #     try:
# #         # Use target job title if provided, otherwise use current job title
# #         target = target_job_title if target_job_title else job_title
# #         skills_text = skills if skills else "relevant technical and soft skills"
# #
# #         # Format the prompt with all details including bullet count
# #         prompt = get_bullet_generation_prompt(
# #             job_title=job_title,
# #             employer=employer,
# #             target_job_title=target,
# #             skills=skills_text,
# #             responsibilities=responsibilities,
# #             bullet_count=bullet_count
# #         )
# #
# #         # Call OpenAI API with new client syntax
# #         response = openai.chat.completions.create(
# #             model="gpt-3.5-turbo",  # You can change this to gpt-4 if available
# #             messages=[
# #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# #                 {"role": "user", "content": prompt}
# #             ],
# #             max_tokens=600,
# #             temperature=0.7,
# #         )
# #
# #         # Extract bullet points from response (updated method)
# #         content = response.choices[0].message.content.strip()
# #         bullets = [line.strip() for line in content.split('\n') if line.strip()]
# #
# #         # Get token usage for cost calculation (updated method)
# #         input_tokens = response.usage.prompt_tokens
# #         output_tokens = response.usage.completion_tokens
# #
# #         # Ensure we have exactly the requested number of bullet points
# #         requested_count = min(max(int(bullet_count), 1), 5)  # Between 1 and 5
# #         if len(bullets) < requested_count:
# #             # Add template bullets if needed
# #             template_bullets = get_template_bullets(job_title, employer)
# #             bullets.extend(template_bullets[:(requested_count - len(bullets))])
# #         elif len(bullets) > requested_count:
# #             bullets = bullets[:requested_count]
# #
# #         return bullets, input_tokens, output_tokens
# #
# #     except Exception as e:
# #         print(f"OpenAI API error: {str(e)}")
# #         # Fallback to template bullets
# #         return get_template_bullets(job_title, employer, bullet_count), 0, 0
# #
# #
# # def enhance_bullet_chatgpt(bullet_text, enhancement_type="general", job_description=""):
# #     """
# #     Enhance a bullet point using OpenAI's GPT models with enhancement type.
# #     Returns the enhanced text and token counts.
# #     """
# #     if not openai.api_key:
# #         return enhance_bullet_basic(bullet_text), 0, 0
# #
# #     try:
# #         # Choose prompt based on enhancement type
# #         if enhancement_type == "ats" and job_description:
# #             prompt = get_ats_optimization_prompt(bullet_text, job_description)
# #         else:
# #             prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)
# #
# #         # Call OpenAI API with new client syntax
# #         response = openai.chat.completions.create(
# #             model="gpt-3.5-turbo",
# #             messages=[
# #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# #                 {"role": "user", "content": prompt}
# #             ],
# #             max_tokens=150,
# #             temperature=0.7,
# #         )
# #
# #         # Extract enhanced text from response (updated method)
# #         enhanced_text = response.choices[0].message.content.strip()
# #
# #         # Get token usage for cost calculation (updated method)
# #         input_tokens = response.usage.prompt_tokens
# #         output_tokens = response.usage.completion_tokens
# #
# #         return enhanced_text, input_tokens, output_tokens
# #
# #     except Exception as e:
# #         print(f"OpenAI API error: {str(e)}")
# #         # Fallback to basic enhancement
# #         return enhance_bullet_basic(bullet_text), 0, 0
# #
# # def generate_bullets_gemini(job_title, employer, target_job_title=None, skills=None, responsibilities=None, bullet_count=3):
# #     """
# #     Generate bullet points using Google's Gemini model with enhanced parameters and customizable count.
# #     Returns the bullet points and token counts.
# #     """
# #     if not genai_api_key:
# #         return get_template_bullets(job_title, employer, bullet_count), 0, 0
# #
# #     try:
# #         # Configure the model
# #         model = genai.GenerativeModel('gemini-pro')
# #
# #         # Use target job title if provided, otherwise use current job title
# #         target = target_job_title if target_job_title else job_title
# #         skills_text = skills if skills else "relevant technical and soft skills"
# #
# #         # Format the prompt with all details including bullet count
# #         prompt = get_bullet_generation_prompt(
# #             job_title=job_title,
# #             employer=employer,
# #             target_job_title=target,
# #             skills=skills_text,
# #             responsibilities=responsibilities,
# #             bullet_count=bullet_count
# #         )
# #
# #         # Call Gemini API
# #         response = model.generate_content(prompt)
# #
# #         # Extract bullet points from response
# #         content = response.text.strip()
# #         bullets = [line.strip() for line in content.split('\n') if line.strip()]
# #
# #         # Gemini doesn't provide token counts directly, so we estimate
# #         # A very rough estimation: 1 token ≈ 4 characters
# #         input_chars = len(prompt)
# #         output_chars = len(content)
# #         input_tokens = input_chars // 4
# #         output_tokens = output_chars // 4
# #
# #         # Ensure we have exactly the requested number of bullet points
# #         requested_count = min(max(int(bullet_count), 1), 5)  # Between 1 and 5
# #         if len(bullets) < requested_count:
# #             # Add template bullets if needed
# #             template_bullets = get_template_bullets(job_title, employer)
# #             bullets.extend(template_bullets[:(requested_count - len(bullets))])
# #         elif len(bullets) > requested_count:
# #             bullets = bullets[:requested_count]
# #
# #         return bullets, input_tokens, output_tokens
# #
# #     except Exception as e:
# #         print(f"Gemini API error: {str(e)}")
# #         # Fallback to template bullets
# #         return get_template_bullets(job_title, employer, bullet_count), 0, 0
# #
# #
# # def enhance_bullet_gemini(bullet_text, enhancement_type="general", job_description=""):
# #     """
# #     Enhance a bullet point using Google's Gemini model with enhancement type.
# #     Returns the enhanced text and token counts.
# #     """
# #     if not genai_api_key:
# #         return enhance_bullet_basic(bullet_text), 0, 0
# #
# #     try:
# #         # Configure the model
# #         model = genai.GenerativeModel('gemini-pro')
# #
# #         # Choose prompt based on enhancement type
# #         if enhancement_type == "ats" and job_description:
# #             prompt = get_ats_optimization_prompt(bullet_text, job_description)
# #         else:
# #             prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)
# #
# #         # Call Gemini API
# #         response = model.generate_content(prompt)
# #
# #         # Extract enhanced text from response
# #         enhanced_text = response.text.strip()
# #
# #         # Gemini doesn't provide token counts directly, so we estimate
# #         # A very rough estimation: 1 token ≈ 4 characters
# #         input_chars = len(prompt)
# #         output_chars = len(enhanced_text)
# #         input_tokens = input_chars // 4
# #         output_tokens = output_chars // 4
# #
# #         return enhanced_text, input_tokens, output_tokens
# #
# #     except Exception as e:
# #         print(f"Gemini API error: {str(e)}")
# #         # Fallback to basic enhancement
# #         return enhance_bullet_basic(bullet_text), 0, 0
# # def ats_optimize_chatgpt(bullet_text, job_description):
# #     """
# #     Optimize a bullet point for ATS systems using OpenAI.
# #     Returns the optimized text and token counts.
# #     """
# #     # This is essentially a specialized version of enhance_bullet_chatgpt
# #     return enhance_bullet_chatgpt(bullet_text, "ats", job_description)
# #
# #
# # def ats_optimize_gemini(bullet_text, job_description):
# #     """
# #     Optimize a bullet point for ATS systems using Gemini.
# #     Returns the optimized text and token counts.
# #     """
# #     # This is essentially a specialized version of enhance_bullet_gemini
# #     return enhance_bullet_gemini(bullet_text, "ats", job_description)
# #
# #
# # # Basic enhancement without AI APIs
# # def enhance_bullet_basic(bullet_text):
# #     """Helper function for basic bullet enhancement without API calls"""
# #     # Example enhancements
# #     enhancements = [
# #         lambda t: t.replace("improved", "significantly improved"),
# #         lambda t: t.replace("increased", "substantially increased"),
# #         lambda t: t.replace("reduced", "dramatically reduced"),
# #         lambda t: t.replace("managed", "successfully managed"),
# #         lambda t: t.replace("developed", "designed and developed"),
# #         lambda t: t + " resulting in significant cost savings" if "cost" not in t.lower() else t,
# #         lambda t: t + " within strict timeline constraints" if "time" not in t.lower() else t,
# #         lambda t: t.replace("team", "cross-functional team"),
# #     ]
# #
# #     # Apply a random enhancement
# #     enhanced_text = bullet_text
# #
# #     # Apply quantitative metrics if none present
# #     if not any(c.isdigit() for c in enhanced_text):
# #         metrics = ["20%", "30%", "25%", "40%", "$50K", "15%"]
# #         improvement_phrases = [
# #             f" resulting in {random.choice(metrics)} improvement in efficiency",
# #             f" leading to {random.choice(metrics)} increase in productivity",
# #             f" generating {random.choice(metrics)} in cost savings",
# #             f" improving customer satisfaction by {random.choice(metrics)}"
# #         ]
# #         enhanced_text += random.choice(improvement_phrases)
# #
# #     # Apply action verb enhancement if needed
# #     action_verbs = ["Developed", "Implemented", "Streamlined", "Spearheaded",
# #                     "Managed", "Executed", "Coordinated", "Led"]
# #
# #     if not any(verb.lower() in enhanced_text.lower()[:15] for verb in action_verbs):
# #         enhanced_text = f"{random.choice(action_verbs)} {enhanced_text[0].lower()}{enhanced_text[1:]}"
# #
# #     # Apply a random generic enhancement
# #     for _ in range(2):  # Apply up to 2 enhancements
# #         enhancement = random.choice(enhancements)
# #         new_text = enhancement(enhanced_text)
# #         if new_text != enhanced_text:  # Only keep if it actually changed something
# #             enhanced_text = new_text
# #             break
# #
# #     return enhanced_text
# #
# #
# # # Template-based bullets for fallback with configurable count
# # def get_template_bullets(job_title, employer, count=3):
# #     """
# #     Helper function to get template bullets based on job title with configurable count.
# #     Count will be between 1 and 5.
# #     """
# #     # Ensure count is between 1 and 5
# #     count = min(max(int(count), 1), 5)
# #
# #     job_bullets = {
# #         'software engineer': [
# #             f"Developed scalable web applications using Python and Django at {employer}, reducing page load times by 45%",
# #             f"Led implementation of CI/CD pipeline at {employer}, decreasing deployment time by 60% and reducing bugs in production by 35%",
# #             f"Optimized database queries for {employer}'s customer portal, resulting in 50% improvement in API response times",
# #             f"Collaborated with cross-functional teams to redesign {employer}'s authentication system, enhancing security while maintaining user experience",
# #             f"Implemented automated testing strategies at {employer}, increasing code coverage by 70% and reducing regression bugs by 40%"
# #         ],
# #         'data scientist': [
# #             f"Analyzed customer data using Python and SQL at {employer}, identifying patterns that increased sales by 28%",
# #             f"Built machine learning models that improved {employer}'s sales forecast accuracy by 40%, directly impacting inventory management",
# #             f"Created interactive dashboards using Tableau for {employer}'s executives, enabling data-driven decisions that reduced costs by $150K annually",
# #             f"Implemented A/B testing framework for {employer}'s marketing campaigns, increasing conversion rates by 35%",
# #             f"Developed NLP algorithms to analyze customer feedback at {employer}, improving product satisfaction scores by 25%"
# #         ],
# #         'project manager': [
# #             f"Led cross-functional teams of 12+ members at {employer}, delivering 5 critical projects on time and under budget",
# #             f"Implemented Agile methodology at {employer}, increasing team productivity by 30% and reducing time-to-market",
# #             f"Managed $1.2M budget for {employer}'s digital transformation initiative, achieving all KPIs while 15% under budget",
# #             f"Developed comprehensive project plans for {employer} that reduced scope creep by 40% and improved stakeholder satisfaction",
# #             f"Streamlined communication processes at {employer}, reducing meeting time by 25% while improving information flow across departments"
# #         ],
# #         'marketing manager': [
# #             f"Developed and executed marketing strategies that increased {employer}'s brand awareness by 45% in key markets",
# #             f"Managed {employer}'s $800K digital marketing budget, achieving 135% of lead generation targets within first 6 months",
# #             f"Launched social media campaigns for {employer} that grew follower base by 75% and engagement by 82%",
# #             f"Conducted market research for {employer}, identifying opportunities that resulted in two product launches generating $2.5M in first-year revenue",
# #             f"Optimized {employer}'s SEO strategy, increasing organic traffic by 65% and reducing cost-per-acquisition by 30%"
# #         ],
# #         'frontend developer': [
# #             f"Developed responsive user interfaces for {employer}'s flagship product using React and TypeScript, increasing user engagement by 38%",
# #             f"Improved web performance at {employer} by implementing code splitting and lazy loading, reducing initial load time by 45%",
# #             f"Collaborated with UX designers to implement intuitive interfaces at {employer}, leading to a 27% improvement in user retention",
# #             f"Refactored legacy codebase at {employer} to modern standards, reducing bundle size by 35% and improving maintainability",
# #             f"Implemented comprehensive UI testing suite for {employer}, decreasing visual regression issues by 60%"
# #         ],
# #         'backend developer': [
# #             f"Designed and implemented RESTful APIs for {employer}'s platform, handling 500K+ daily requests with 99.9% uptime",
# #             f"Optimized database architecture at {employer}, reducing query times by 65% and improving system scalability",
# #             f"Implemented microservices architecture at {employer}, enabling 3x faster feature deployment and improved system resilience",
# #             f"Developed authentication and authorization system for {employer}, enhancing security while maintaining excellent user experience",
# #             f"Created automated data processing pipelines at {employer}, reducing manual work by 80% and ensuring data integrity"
# #         ],
# #         'data analyst': [
# #             f"Analyzed customer behavior data at {employer}, identifying patterns that led to a 32% increase in customer retention",
# #             f"Created automated reporting dashboards for {employer}, saving 15+ hours weekly and improving data visibility across departments",
# #             f"Conducted in-depth market analysis for {employer}, informing strategic decisions that increased quarterly revenue by 18%",
# #             f"Implemented improved data collection methods at {employer}, increasing data accuracy by 45% and reducing missing data points",
# #             f"Developed statistical models for {employer} that predicted customer churn with 85% accuracy, enabling proactive retention measures"
# #         ],
# #         'product manager': [
# #             f"Led development of key product features at {employer}, increasing user adoption by 40% and reducing churn by 25%",
# #             f"Conducted comprehensive market analysis for {employer}, identifying unmet customer needs that led to 3 successful product launches",
# #             f"Created and managed product roadmap at {employer}, aligning stakeholder expectations and delivering all milestones on schedule",
# #             f"Implemented customer feedback loops at {employer}, resulting in 35% higher customer satisfaction and improved product-market fit",
# #             f"Coordinated cross-functional team of 15 members at {employer}, streamlining product development lifecycle by 30%"
# #         ]
# #     }
# #
# #     # Normalize job title for matching
# #     job_title_lower = job_title.lower()
# #
# #     # Get the appropriate bullet points based on job title or use generic ones
# #     job_key = next((key for key in job_bullets if key in job_title_lower), None)
# #
# #     if job_key:
# #         return job_bullets[job_key][:count]
# #     else:
# #         # Generic bullet points for any job
# #         generic_bullets = [
# #             f"Spearheaded key initiatives at {employer} that improved operational efficiency by 20% and reduced annual costs by $45K",
# #             f"Collaborated with cross-functional teams at {employer} to implement best practices and streamline workflows, increasing productivity by 25%",
# #             f"Managed multiple projects simultaneously at {employer}, meeting 100% of deadlines while maintaining exceptional quality standards",
# #             f"Recognized for outstanding performance at {employer}, receiving commendation from senior leadership for contributions to company growth",
# #             f"Implemented innovative solutions at {employer} that resolved critical business challenges and improved customer satisfaction by 30%"
# #         ]
# #         return generic_bullets[:count]
# #
# #
# # # # ai_services.py
# # # import time
# # # import random
# # # import openai
# # # import google.generativeai as genai
# # # from django.conf import settings
# # #
# # # # Initialize APIs if keys are available
# # # openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
# # # genai_api_key = getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
# # # if genai_api_key:
# # #     genai.configure(api_key=genai_api_key)
# # #
# # # # Updated prompts with more ATS focus
# # # RESUME_WRITER_SYSTEM_MESSAGE = """You are an expert resume writer specializing in ATS-optimized resumes.
# # # Your task is to create impactful bullet points that highlight achievements, incorporate relevant skills,
# # # and use industry-specific keywords that will pass through Applicant Tracking Systems."""
# # #
# # #
# # # # Enhanced prompt for bullet generation with more parameters
# # # def get_bullet_generation_prompt(job_title, employer, target_job_title, skills, responsibilities=None):
# # #     prompt = f"""Generate 4 professional resume bullet points for a {job_title} position at {employer}
# # # that would be highly effective for applying to a {target_job_title} position.
# # #
# # # Incorporate these skills where relevant: {skills}
# # #
# # # """
# # #
# # #     if responsibilities:
# # #         prompt += f"""
# # # Based on these responsibilities/achievements: {responsibilities}
# # # """
# # #
# # #     prompt += """
# # # Each bullet point should:
# # # 1. Start with a strong action verb
# # # 2. Include measurable achievements with specific numbers (%, $, etc.)
# # # 3. Be concise (100-150 characters optimal)
# # # 4. Focus on accomplishments rather than just responsibilities
# # # 5. Include keywords relevant to the target position
# # # 6. Be optimized for Applicant Tracking Systems (ATS)
# # #
# # # Format the response as a simple list with one bullet point per line.
# # # Do not include bullet markers, numbers, or any other formatting."""
# # #
# # #     return prompt
# # #
# # #
# # # # Enhanced bullet enhancement prompt
# # # def get_bullet_enhancement_prompt(bullet_text, enhancement_type="general"):
# # #     if enhancement_type == "ats":
# # #         return f"""Optimize the following resume bullet point specifically for Applicant Tracking Systems (ATS):
# # #
# # # Original: {bullet_text}
# # #
# # # Instructions:
# # # 1. Ensure it includes industry-standard keywords that ATS systems typically scan for
# # # 2. Keep a strong action verb at the beginning
# # # 3. Maintain quantifiable achievements and metrics
# # # 4. Ensure it remains clear and readable for humans
# # # 5. Keep it concise yet impactful (100-150 characters optimal)
# # # 6. Do not add any fictional achievements or details
# # #
# # # Provide only the optimized bullet point text with no additional commentary."""
# # #
# # #     else:  # general enhancement
# # #         return f"""Enhance the following resume bullet point to be more impactful:
# # #
# # # Original: {bullet_text}
# # #
# # # Instructions:
# # # 1. Ensure it starts with a strong action verb
# # # 2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
# # # 3. Focus on achievements rather than responsibilities
# # # 4. Keep it concise yet impactful (100-150 characters optimal)
# # # 5. Maintain professional language and clarity
# # # 6. Do not add any fictional achievements or details
# # #
# # # Provide only the enhanced bullet point text with no additional commentary."""
# # #
# # #
# # # # ATS optimization prompt with job description
# # # def get_ats_optimization_prompt(bullet_text, job_description=''):
# # #     prompt = f"""Optimize the following resume bullet point for Applicant Tracking Systems (ATS):
# # #
# # # Original bullet point: {bullet_text}
# # #
# # # """
# # #
# # #     if job_description:
# # #         prompt += f"""Target Job Description:
# # # {job_description}
# # #
# # # """
# # #
# # #     prompt += """Instructions:
# # # 1. Include relevant keywords from the job description when available
# # # 2. Keep the strong action verb at the beginning
# # # 3. Maintain quantifiable achievements and metrics
# # # 4. Ensure it remains clear and readable for humans
# # # 5. Keep it concise yet impactful
# # # 6. Do not add any fictional achievements or details
# # #
# # # Provide only the optimized bullet point text with no additional commentary."""
# # #
# # #     return prompt
# # #
# # # #
# # # # # ChatGPT Service Functions
# # # # def generate_bullets_chatgpt(job_title, employer, target_job_title=None, skills=None, responsibilities=None):
# # # #     """
# # # #     Generate bullet points using OpenAI's GPT models with enhanced parameters.
# # # #     Returns the bullet points and token counts.
# # # #     """
# # # #     if not openai.api_key:
# # # #         return get_template_bullets(job_title, employer), 0, 0
# # # #
# # # #     try:
# # # #         # Use target job title if provided, otherwise use current job title
# # # #         target = target_job_title if target_job_title else job_title
# # # #         skills_text = skills if skills else "relevant technical and soft skills"
# # # #
# # # #         # Format the prompt with all details
# # # #         prompt = get_bullet_generation_prompt(
# # # #             job_title=job_title,
# # # #             employer=employer,
# # # #             target_job_title=target,
# # # #             skills=skills_text,
# # # #             responsibilities=responsibilities
# # # #         )
# # # #
# # # #         # Call OpenAI API
# # # #         response = openai.ChatCompletion.create(
# # # #             model="gpt-3.5-turbo",  # You can change this to gpt-4 if available
# # # #             messages=[
# # # #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# # # #                 {"role": "user", "content": prompt}
# # # #             ],
# # # #             max_tokens=600,
# # # #             temperature=0.7,
# # # #         )
# # # #
# # # #         # Extract bullet points from response
# # # #         content = response.choices[0].message.content.strip()
# # # #         bullets = [line.strip() for line in content.split('\n') if line.strip()]
# # # #
# # # #         # Get token usage for cost calculation
# # # #         input_tokens = response.usage.prompt_tokens
# # # #         output_tokens = response.usage.completion_tokens
# # # #
# # # #         # Ensure we have exactly 4 bullet points
# # # #         if len(bullets) < 4:
# # # #             # Add template bullets if needed
# # # #             template_bullets = get_template_bullets(job_title, employer)
# # # #             bullets.extend(template_bullets[:(4 - len(bullets))])
# # # #         elif len(bullets) > 4:
# # # #             bullets = bullets[:4]
# # # #
# # # #         return bullets, input_tokens, output_tokens
# # # #
# # # #     except Exception as e:
# # # #         print(f"OpenAI API error: {str(e)}")
# # # #         # Fallback to template bullets
# # # #         return get_template_bullets(job_title, employer), 0, 0
# # # #
# # # #
# # # # def enhance_bullet_chatgpt(bullet_text, enhancement_type="general", job_description=""):
# # # #     """
# # # #     Enhance a bullet point using OpenAI's GPT models with enhancement type.
# # # #     Returns the enhanced text and token counts.
# # # #     """
# # # #     if not openai.api_key:
# # # #         return enhance_bullet_basic(bullet_text), 0, 0
# # # #
# # # #     try:
# # # #         # Choose prompt based on enhancement type
# # # #         if enhancement_type == "ats" and job_description:
# # # #             prompt = get_ats_optimization_prompt(bullet_text, job_description)
# # # #         else:
# # # #             prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)
# # # #
# # # #         # Call OpenAI API
# # # #         response = openai.ChatCompletion.create(
# # # #             model="gpt-3.5-turbo",
# # # #             messages=[
# # # #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# # # #                 {"role": "user", "content": prompt}
# # # #             ],
# # # #             max_tokens=150,
# # # #             temperature=0.7,
# # # #         )
# # # #
# # # #         # Extract enhanced text from response
# # # #         enhanced_text = response.choices[0].message.content.strip()
# # # #
# # # #         # Get token usage for cost calculation
# # # #         input_tokens = response.usage.prompt_tokens
# # # #         output_tokens = response.usage.completion_tokens
# # # #
# # # #         return enhanced_text, input_tokens, output_tokens
# # # #
# # # #     except Exception as e:
# # # #         print(f"OpenAI API error: {str(e)}")
# # # #         # Fallback to basic enhancement
# # # #         return enhance_bullet_basic(bullet_text), 0, 0
# # #
# # # def generate_bullets_chatgpt(job_title, employer, target_job_title=None, skills=None, responsibilities=None):
# # #     """
# # #     Generate bullet points using OpenAI's GPT models with enhanced parameters.
# # #     Returns the bullet points and token counts.
# # #     """
# # #     if not openai.api_key:
# # #         return get_template_bullets(job_title, employer), 0, 0
# # #
# # #     try:
# # #         # Use target job title if provided, otherwise use current job title
# # #         target = target_job_title if target_job_title else job_title
# # #         skills_text = skills if skills else "relevant technical and soft skills"
# # #
# # #         # Format the prompt with all details
# # #         prompt = get_bullet_generation_prompt(
# # #             job_title=job_title,
# # #             employer=employer,
# # #             target_job_title=target,
# # #             skills=skills_text,
# # #             responsibilities=responsibilities
# # #         )
# # #
# # #         # Call OpenAI API with new client syntax
# # #         response = openai.chat.completions.create(
# # #             model="gpt-3.5-turbo",  # You can change this to gpt-4 if available
# # #             messages=[
# # #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# # #                 {"role": "user", "content": prompt}
# # #             ],
# # #             max_tokens=600,
# # #             temperature=0.7,
# # #         )
# # #
# # #         # Extract bullet points from response (updated method)
# # #         content = response.choices[0].message.content.strip()
# # #         bullets = [line.strip() for line in content.split('\n') if line.strip()]
# # #
# # #         # Get token usage for cost calculation (updated method)
# # #         input_tokens = response.usage.prompt_tokens
# # #         output_tokens = response.usage.completion_tokens
# # #
# # #         # Ensure we have exactly 4 bullet points
# # #         if len(bullets) < 4:
# # #             # Add template bullets if needed
# # #             template_bullets = get_template_bullets(job_title, employer)
# # #             bullets.extend(template_bullets[:(4 - len(bullets))])
# # #         elif len(bullets) > 4:
# # #             bullets = bullets[:4]
# # #
# # #         return bullets, input_tokens, output_tokens
# # #
# # #     except Exception as e:
# # #         print(f"OpenAI API error: {str(e)}")
# # #         # Fallback to template bullets
# # #         return get_template_bullets(job_title, employer), 0, 0
# # #
# # #
# # # def enhance_bullet_chatgpt(bullet_text, enhancement_type="general", job_description=""):
# # #     """
# # #     Enhance a bullet point using OpenAI's GPT models with enhancement type.
# # #     Returns the enhanced text and token counts.
# # #     """
# # #     if not openai.api_key:
# # #         return enhance_bullet_basic(bullet_text), 0, 0
# # #
# # #     try:
# # #         # Choose prompt based on enhancement type
# # #         if enhancement_type == "ats" and job_description:
# # #             prompt = get_ats_optimization_prompt(bullet_text, job_description)
# # #         else:
# # #             prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)
# # #
# # #         # Call OpenAI API with new client syntax
# # #         response = openai.chat.completions.create(
# # #             model="gpt-3.5-turbo",
# # #             messages=[
# # #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# # #                 {"role": "user", "content": prompt}
# # #             ],
# # #             max_tokens=150,
# # #             temperature=0.7,
# # #         )
# # #
# # #         # Extract enhanced text from response (updated method)
# # #         enhanced_text = response.choices[0].message.content.strip()
# # #
# # #         # Get token usage for cost calculation (updated method)
# # #         input_tokens = response.usage.prompt_tokens
# # #         output_tokens = response.usage.completion_tokens
# # #
# # #         return enhanced_text, input_tokens, output_tokens
# # #
# # #     except Exception as e:
# # #         print(f"OpenAI API error: {str(e)}")
# # #         # Fallback to basic enhancement
# # #         return enhance_bullet_basic(bullet_text), 0, 0
# # #
# # #
# # # # Gemini Service Functions
# # # def generate_bullets_gemini(job_title, employer, target_job_title=None, skills=None, responsibilities=None):
# # #     """
# # #     Generate bullet points using Google's Gemini model with enhanced parameters.
# # #     Returns the bullet points and token counts.
# # #     """
# # #     if not genai_api_key:
# # #         return get_template_bullets(job_title, employer), 0, 0
# # #
# # #     try:
# # #         # Configure the model
# # #         model = genai.GenerativeModel('gemini-pro')
# # #
# # #         # Use target job title if provided, otherwise use current job title
# # #         target = target_job_title if target_job_title else job_title
# # #         skills_text = skills if skills else "relevant technical and soft skills"
# # #
# # #         # Format the prompt with all details
# # #         prompt = get_bullet_generation_prompt(
# # #             job_title=job_title,
# # #             employer=employer,
# # #             target_job_title=target,
# # #             skills=skills_text,
# # #             responsibilities=responsibilities
# # #         )
# # #
# # #         # Call Gemini API
# # #         response = model.generate_content(prompt)
# # #
# # #         # Extract bullet points from response
# # #         content = response.text.strip()
# # #         bullets = [line.strip() for line in content.split('\n') if line.strip()]
# # #
# # #         # Gemini doesn't provide token counts directly, so we estimate
# # #         # A very rough estimation: 1 token ≈ 4 characters
# # #         input_chars = len(prompt)
# # #         output_chars = len(content)
# # #         input_tokens = input_chars // 4
# # #         output_tokens = output_chars // 4
# # #
# # #         # Ensure we have exactly 4 bullet points
# # #         if len(bullets) < 4:
# # #             # Add template bullets if needed
# # #             template_bullets = get_template_bullets(job_title, employer)
# # #             bullets.extend(template_bullets[:(4 - len(bullets))])
# # #         elif len(bullets) > 4:
# # #             bullets = bullets[:4]
# # #
# # #         return bullets, input_tokens, output_tokens
# # #
# # #     except Exception as e:
# # #         print(f"Gemini API error: {str(e)}")
# # #         # Fallback to template bullets
# # #         return get_template_bullets(job_title, employer), 0, 0
# # #
# # #
# # # def enhance_bullet_gemini(bullet_text, enhancement_type="general", job_description=""):
# # #     """
# # #     Enhance a bullet point using Google's Gemini model with enhancement type.
# # #     Returns the enhanced text and token counts.
# # #     """
# # #     if not genai_api_key:
# # #         return enhance_bullet_basic(bullet_text), 0, 0
# # #
# # #     try:
# # #         # Configure the model
# # #         model = genai.GenerativeModel('gemini-pro')
# # #
# # #         # Choose prompt based on enhancement type
# # #         if enhancement_type == "ats" and job_description:
# # #             prompt = get_ats_optimization_prompt(bullet_text, job_description)
# # #         else:
# # #             prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)
# # #
# # #         # Call Gemini API
# # #         response = model.generate_content(prompt)
# # #
# # #         # Extract enhanced text from response
# # #         enhanced_text = response.text.strip()
# # #
# # #         # Gemini doesn't provide token counts directly, so we estimate
# # #         # A very rough estimation: 1 token ≈ 4 characters
# # #         input_chars = len(prompt)
# # #         output_chars = len(enhanced_text)
# # #         input_tokens = input_chars // 4
# # #         output_tokens = output_chars // 4
# # #
# # #         return enhanced_text, input_tokens, output_tokens
# # #
# # #     except Exception as e:
# # #         print(f"Gemini API error: {str(e)}")
# # #         # Fallback to basic enhancement
# # #         return enhance_bullet_basic(bullet_text), 0, 0
# # #
# # #
# # # def ats_optimize_chatgpt(bullet_text, job_description):
# # #     """
# # #     Optimize a bullet point for ATS systems using OpenAI.
# # #     Returns the optimized text and token counts.
# # #     """
# # #     # This is essentially a specialized version of enhance_bullet_chatgpt
# # #     return enhance_bullet_chatgpt(bullet_text, "ats", job_description)
# # #
# # #
# # # def ats_optimize_gemini(bullet_text, job_description):
# # #     """
# # #     Optimize a bullet point for ATS systems using Gemini.
# # #     Returns the optimized text and token counts.
# # #     """
# # #     # This is essentially a specialized version of enhance_bullet_gemini
# # #     return enhance_bullet_gemini(bullet_text, "ats", job_description)
# # #
# # #
# # # # Basic enhancement without AI APIs
# # # def enhance_bullet_basic(bullet_text):
# # #     """Helper function for basic bullet enhancement without API calls"""
# # #     # Example enhancements
# # #     enhancements = [
# # #         lambda t: t.replace("improved", "significantly improved"),
# # #         lambda t: t.replace("increased", "substantially increased"),
# # #         lambda t: t.replace("reduced", "dramatically reduced"),
# # #         lambda t: t.replace("managed", "successfully managed"),
# # #         lambda t: t.replace("developed", "designed and developed"),
# # #         lambda t: t + " resulting in significant cost savings" if "cost" not in t.lower() else t,
# # #         lambda t: t + " within strict timeline constraints" if "time" not in t.lower() else t,
# # #         lambda t: t.replace("team", "cross-functional team"),
# # #     ]
# # #
# # #     # Apply a random enhancement
# # #     enhanced_text = bullet_text
# # #
# # #     # Apply quantitative metrics if none present
# # #     if not any(c.isdigit() for c in enhanced_text):
# # #         metrics = ["20%", "30%", "25%", "40%", "$50K", "15%"]
# # #         improvement_phrases = [
# # #             f" resulting in {random.choice(metrics)} improvement in efficiency",
# # #             f" leading to {random.choice(metrics)} increase in productivity",
# # #             f" generating {random.choice(metrics)} in cost savings",
# # #             f" improving customer satisfaction by {random.choice(metrics)}"
# # #         ]
# # #         enhanced_text += random.choice(improvement_phrases)
# # #
# # #     # Apply action verb enhancement if needed
# # #     action_verbs = ["Developed", "Implemented", "Streamlined", "Spearheaded",
# # #                     "Managed", "Executed", "Coordinated", "Led"]
# # #
# # #     if not any(verb.lower() in enhanced_text.lower()[:15] for verb in action_verbs):
# # #         enhanced_text = f"{random.choice(action_verbs)} {enhanced_text[0].lower()}{enhanced_text[1:]}"
# # #
# # #     # Apply a random generic enhancement
# # #     for _ in range(2):  # Apply up to 2 enhancements
# # #         enhancement = random.choice(enhancements)
# # #         new_text = enhancement(enhanced_text)
# # #         if new_text != enhanced_text:  # Only keep if it actually changed something
# # #             enhanced_text = new_text
# # #             break
# # #
# # #     return enhanced_text
# # #
# # #
# # # # Template-based bullets for fallback
# # # def get_template_bullets(job_title, employer):
# # #     """Helper function to get template bullets based on job title"""
# # #     job_bullets = {
# # #         'software engineer': [
# # #             f"Developed scalable web applications using Python and Django at {employer}, reducing page load times by 45%",
# # #             f"Led implementation of CI/CD pipeline at {employer}, decreasing deployment time by 60% and reducing bugs in production by 35%",
# # #             f"Optimized database queries for {employer}'s customer portal, resulting in 50% improvement in API response times",
# # #             f"Collaborated with cross-functional teams to redesign {employer}'s authentication system, enhancing security while maintaining user experience"
# # #         ],
# # #         'data scientist': [
# # #             f"Analyzed customer data using Python and SQL at {employer}, identifying patterns that increased sales by 28%",
# # #             f"Built machine learning models that improved {employer}'s sales forecast accuracy by 40%, directly impacting inventory management",
# # #             f"Created interactive dashboards using Tableau for {employer}'s executives, enabling data-driven decisions that reduced costs by $150K annually",
# # #             f"Implemented A/B testing framework for {employer}'s marketing campaigns, increasing conversion rates by 35%"
# # #         ],
# # #         'project manager': [
# # #             f"Led cross-functional teams of 12+ members at {employer}, delivering 5 critical projects on time and under budget",
# # #             f"Implemented Agile methodology at {employer}, increasing team productivity by 30% and reducing time-to-market",
# # #             f"Managed $1.2M budget for {employer}'s digital transformation initiative, achieving all KPIs while 15% under budget",
# # #             f"Developed comprehensive project plans for {employer} that reduced scope creep by 40% and improved stakeholder satisfaction"
# # #         ],
# # #         'marketing manager': [
# # #             f"Developed and executed marketing strategies that increased {employer}'s brand awareness by 45% in key markets",
# # #             f"Managed {employer}'s $800K digital marketing budget, achieving 135% of lead generation targets within first 6 months",
# # #             f"Launched social media campaigns for {employer} that grew follower base by 75% and engagement by 82%",
# # #             f"Conducted market research for {employer}, identifying opportunities that resulted in two product launches generating $2.5M in first-year revenue"
# # #         ]
# # #     }
# # #
# # #     # Normalize job title for matching
# # #     job_title_lower = job_title.lower()
# # #
# # #     # Get the appropriate bullet points based on job title or use generic ones
# # #     job_key = next((key for key in job_bullets if key in job_title_lower), None)
# # #
# # #     if job_key:
# # #         return job_bullets[job_key]
# # #     else:
# # #         # Generic bullet points for any job
# # #         return [
# # #             f"Spearheaded key initiatives at {employer} that improved operational efficiency by 20% and reduced annual costs by $45K",
# # #             f"Collaborated with cross-functional teams at {employer} to implement best practices and streamline workflows, increasing productivity by 25%",
# # #             f"Managed multiple projects simultaneously at {employer}, meeting 100% of deadlines while maintaining exceptional quality standards",
# # #             f"Recognized for outstanding performance at {employer}, receiving commendation from senior leadership for contributions to company growth"
# # #         ]