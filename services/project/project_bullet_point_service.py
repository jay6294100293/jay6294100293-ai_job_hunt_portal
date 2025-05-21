# services/project/project_bullet_point_service.py

import time
import logging
import openai
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Enhancement Prompts for Project Bullet Points
PROJECT_ENHANCEMENT_SYSTEM_MESSAGE = """You are an expert resume writer specializing in optimizing project descriptions
for job applications. Your task is to enhance bullet points to be impactful,
keyword-rich, and focused on measurable achievements and technical skills."""


def get_project_enhancement_prompt(bullet_text, project_name, project_summary="", enhancement_type="general"):
    """
    Get the prompt for enhancing project bullet points without requiring project_title/employer.

    Args:
        bullet_text (str): The original bullet point text
        project_name (str): The name of the project
        project_summary (str): Optional summary of the project
        enhancement_type (str): Type of enhancement ('general' or 'ats')

    Returns:
        str: The formatted prompt
    """
    # Base context about the project
    project_context = f"""
Project Name: {project_name}
"""
    if project_summary:
        project_context += f"Project Summary: {project_summary}\n"

    if enhancement_type == "ats":
        return f"""Enhance the following project bullet point to be more impactful for ATS systems:

{project_context}

Original Bullet Point: {bullet_text}

Instructions:
1. Ensure it starts with a strong action verb
2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
3. Include relevant technical keywords that ATS systems typically scan for
4. Focus on achievements and impact rather than just responsibilities
5. Maintain professional language and clarity
6. Keep it concise yet impactful (100-150 characters optimal)
7. Do not add any fictional achievements or details

Provide only the enhanced bullet point text with no additional commentary."""

    else:  # general enhancement
        return f"""Enhance the following project bullet point to be more impactful:

{project_context}

Original Bullet Point: {bullet_text}

Instructions:
1. Ensure it starts with a strong action verb
2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
3. Focus on achievements and impact rather than just responsibilities
4. Keep it concise yet impactful (100-150 characters optimal)
5. Incorporate the project context to make it more relevant
6. Maintain professional language and clarity
7. Do not add any fictional achievements or details

Provide only the enhanced bullet point text with no additional commentary."""


def enhance_project_bullet_chatgpt(bullet_text, project_title, project_name, project_summary="",
                                   enhancement_type="general"):
    """
    Enhance a project bullet point using OpenAI's ChatGPT.

    Args:
        bullet_text (str): The original bullet point text
        project_title (str): The job title of the user (kept for backward compatibility)
        project_name (str): The name of the project
        project_summary (str): Optional summary of the project
        enhancement_type (str): Type of enhancement ('general' or 'ats')

    Returns:
        tuple: (enhanced_text, input_tokens, output_tokens)
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        return f"Error: OpenAI API key not configured. Please provide your API key in account settings. Original: {bullet_text}", 0, 0

    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)

        # Generate the prompt with project context
        prompt = get_project_enhancement_prompt(
            bullet_text,
            project_name,
            project_summary,
            enhancement_type
        )

        # Call OpenAI API
        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": PROJECT_ENHANCEMENT_SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )

        # Extract enhanced text from response
        enhanced_text = response.choices[0].message.content.strip()

        # Get token usage for cost calculation
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        return enhanced_text, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        # Return original text with error message
        return f"Error enhancing with ChatGPT: {str(e)}. Original: {bullet_text}", 0, 0


def enhance_project_bullet_gemini(bullet_text, project_title, project_name, project_summary="",
                                  enhancement_type="general"):
    """
    Enhance a project bullet point using Google's Gemini model.

    Args:
        bullet_text (str): The original bullet point text
        project_title (str): The job title of the user (kept for backward compatibility)
        project_name (str): The name of the project
        project_summary (str): Optional summary of the project
        enhancement_type (str): Type of enhancement ('general' or 'ats')

    Returns:
        tuple: (enhanced_text, input_tokens, output_tokens)
    """
    api_key = getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
    if not api_key:
        return f"Error: Gemini API key not configured. Please provide your API key in account settings. Original: {bullet_text}", 0, 0

    try:
        # Configure the model
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(getattr(settings, 'GEMINI_MODEL', 'gemini-pro'))

        # Generate the prompt with project context
        prompt = get_project_enhancement_prompt(
            bullet_text,
            project_name,
            project_summary,
            enhancement_type
        )

        # Call Gemini API
        response = model.generate_content(prompt)

        # Extract enhanced text from response
        enhanced_text = response.text.strip()

        # Gemini doesn't provide token counts directly, so we estimate
        # A very rough estimation: 1 token ≈ 4 characters
        input_chars = len(prompt)
        output_chars = len(enhanced_text)
        input_tokens = input_chars // 4
        output_tokens = output_chars // 4

        return enhanced_text, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        # Return original text with error message
        return f"Error enhancing with Gemini: {str(e)}. Original: {bullet_text}", 0, 0
# # File: services/project/project_bullet_point_service.py
#
# import openai
# import google.generativeai as genai
# import json
# import logging
# from django.conf import settings  # Still needed for settings.OPENAI_MODEL
# from services.prompts import experience_prompts
#
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
#             logger.warning("OpenAI API key was not provided by the user for project service.")
#             return None
#         try:
#             return openai.OpenAI(api_key=self.user_openai_key)
#         except Exception as e:
#             logger.error(f"Failed to initialize OpenAI client for project service with user-provided key: {e}")
#             return None
#
#     def _get_gemini_client(self):
#         if not self.user_gemini_key:
#             logger.warning("Gemini API key was not provided by the user for project service.")
#             return None
#         try:
#             genai.configure(api_key=self.user_gemini_key)
#             # Ensure you are using a model that supports the generate_content method as used.
#             return genai.GenerativeModel(
#                 settings.GEMINI_MODEL_NAME if hasattr(settings, 'GEMINI_MODEL_NAME') else 'gemini-pro')
#         except Exception as e:
#             logger.error(f"Failed to initialize Gemini client for project service with user-provided key: {e}")
#             return None
#
#     def generate_project_bullet_points(self, project_name, project_description, project_technologies, tone, count=3,
#                                        ai_provider="gemini"):
#         if ai_provider == "openai" and not self.openai_client:
#             return {"error": "OpenAI client not initialized. Please provide your OpenAI API key."}
#         if ai_provider == "gemini" and not self.gemini_client:
#             return {"error": "Gemini client not initialized. Please provide your Gemini API key."}
#
#         try:
#             context_prompt = experience_prompts.PROJECT_DESCRIPTION_PROMPT.format(
#                 project_name=project_name,
#                 project_description=project_description,
#                 project_technologies=project_technologies,
#                 tone=tone,
#                 bullet_point_count=count
#             )
#
#             final_prompt = experience_prompts.GENERATE_PROJECT_BULLET_POINTS_PROMPT.format(
#                 original_project_description=context_prompt,
#                 project_name=project_name,
#                 technologies_used=", ".join(project_technologies) if isinstance(project_technologies,
#                                                                                 list) else project_technologies,
#                 tone=tone,
#                 count=count
#             )
#             logger.debug(f"Generating project bullet points with {ai_provider}. User-provided key used.")
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
#         except json.JSONDecodeError as e:
#             logger.error(f"JSONDecodeError in generate_project_bullet_points ({ai_provider}): {e}")
#             raw_response = "Unavailable"
#             if 'response' in locals():
#                 if ai_provider == "openai" and hasattr(response, 'choices') and response.choices:
#                     raw_response = response.choices[0].message.content
#                 elif ai_provider == "gemini" and hasattr(response, 'text'):
#                     raw_response = response.text
#             logger.error(f"Raw response from {ai_provider} was: {raw_response}")
#             return {"error": f"Failed to decode AI response. Raw response: {raw_response}"}
#         except Exception as e:
#             logger.error(f"Error processing with {ai_provider} in generate_project_bullet_points: {e}")
#             return {"error": f"An error occurred with {ai_provider}: {str(e)}"}
#
#     def enhance_project_bullet_points(self, project_name, project_description, project_technologies, bullet_points,
#                                       tone, ai_provider="gemini"):
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
#             final_prompt = experience_prompts.ENHANCE_PROJECT_BULLET_POINTS_PROMPT.format(
#                 project_name=project_name,
#                 project_description=project_description,
#                 technologies_used=", ".join(project_technologies) if isinstance(project_technologies,
#                                                                                 list) else project_technologies,
#                 bullet_points=bullet_points_str,
#                 tone=tone
#             )
#             logger.debug(f"Enhancing project bullet points with {ai_provider}. User-provided key used.")
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
#         except json.JSONDecodeError as e:
#             logger.error(f"JSONDecodeError in enhance_project_bullet_points ({ai_provider}): {e}")
#             raw_response = "Unavailable"
#             if 'response' in locals():
#                 if ai_provider == "openai" and hasattr(response, 'choices') and response.choices:
#                     raw_response = response.choices[0].message.content
#                 elif ai_provider == "gemini" and hasattr(response, 'text'):
#                     raw_response = response.text
#             logger.error(f"Raw response from {ai_provider} was: {raw_response}")
#             return {"error": f"Failed to decode AI response. Raw response: {raw_response}"}
#         except Exception as e:
#             logger.error(f"Error processing with {ai_provider} in enhance_project_bullet_points: {e}")
#             return {"error": f"An error occurred with {ai_provider}: {str(e)}"}
#
# # # services/project_enhancement_service.py
# #
# # import time
# # import openai
# # import google.generativeai as genai
# # from django.conf import settings
# # from job_portal.models import APIUsage
# #
# # # Initialize APIs if keys are available
# # openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
# # genai_api_key = getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
# # if genai_api_key:
# #     genai.configure(api_key=genai_api_key)
# #
# # # System message for AI
# # PROJECT_ENHANCEMENT_SYSTEM_MESSAGE = """You are an expert resume writer specializing in optimizing project descriptions
# # for job applications. Your task is to enhance bullet points to be impactful,
# # keyword-rich, and focused on measurable achievements and technical skills."""
# #
# #
# # def get_project_enhancement_prompt(bullet_text, project_title, project_name, project_summary="",
# #                                    enhancement_type="general"):
# #     """
# #     Get the prompt for enhancing project bullet points.
# #
# #     Args:
# #         bullet_text (str): The original bullet point text
# #         project_title (str): The job title of the user
# #         project_name (str): The name of the project
# #         project_summary (str): Optional summary of the project
# #         enhancement_type (str): Type of enhancement ('general' or 'ats')
# #
# #     Returns:
# #         str: The formatted prompt
# #     """
# #     # Base context about the project
# #     project_context = f"""
# # Project Name: {project_name}
# # """
# #     if project_title:
# #         project_context += f"Role/Title: {project_title}\n"
# #
# #     if project_summary:
# #         project_context += f"Project Summary: {project_summary}\n"
# #
# #     if enhancement_type == "ats":
# #         return f"""Enhance the following project bullet point to be more impactful for ATS systems:
# #
# # {project_context}
# #
# # Original Bullet Point: {bullet_text}
# #
# # Instructions:
# # 1. Ensure it starts with a strong action verb
# # 2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
# # 3. Include relevant technical keywords that ATS systems typically scan for
# # 4. Focus on achievements and impact rather than just responsibilities
# # 5. Maintain professional language and clarity
# # 6. Keep it concise yet impactful (100-150 characters optimal)
# # 7. Do not add any fictional achievements or details
# #
# # Provide only the enhanced bullet point text with no additional commentary."""
# #
# #     else:  # general enhancement
# #         return f"""Enhance the following project bullet point to be more impactful:
# #
# # {project_context}
# #
# # Original Bullet Point: {bullet_text}
# #
# # Instructions:
# # 1. Ensure it starts with a strong action verb
# # 2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
# # 3. Focus on achievements and impact rather than just responsibilities
# # 4. Keep it concise yet impactful (100-150 characters optimal)
# # 5. Incorporate the project context to make it more relevant
# # 6. Maintain professional language and clarity
# # 7. Do not add any fictional achievements or details
# #
# # Provide only the enhanced bullet point text with no additional commentary."""
# #
# #
# # def enhance_project_bullet_chatgpt(bullet_text, project_title, project_name, project_summary="",
# #                                    enhancement_type="general"):
# #     """
# #     Enhance a project bullet point using OpenAI's ChatGPT.
# #
# #     Args:
# #         bullet_text (str): The original bullet point text
# #         project_title (str): The job title of the user
# #         project_name (str): The name of the project
# #         project_summary (str): Optional summary of the project
# #         enhancement_type (str): Type of enhancement ('general' or 'ats')
# #
# #     Returns:
# #         tuple: (enhanced_text, input_tokens, output_tokens)
# #     """
# #     if not openai.api_key:
# #         return bullet_text, 0, 0
# #
# #     try:
# #         # Generate the prompt with project context
# #         prompt = get_project_enhancement_prompt(
# #             bullet_text,
# #             project_title,
# #             project_name,
# #             project_summary,
# #             enhancement_type
# #         )
# #
# #         # Call OpenAI API
# #         response = openai.chat.completions.create(
# #             model="gpt-3.5-turbo",
# #             messages=[
# #                 {"role": "system", "content": PROJECT_ENHANCEMENT_SYSTEM_MESSAGE},
# #                 {"role": "user", "content": prompt}
# #             ],
# #             max_tokens=200,
# #             temperature=0.7,
# #         )
# #
# #         # Extract enhanced text from response
# #         enhanced_text = response.choices[0].message.content.strip()
# #
# #         # Get token usage for cost calculation
# #         input_tokens = response.usage.prompt_tokens
# #         output_tokens = response.usage.completion_tokens
# #
# #         return enhanced_text, input_tokens, output_tokens
# #
# #     except Exception as e:
# #         print(f"OpenAI API error: {str(e)}")
# #         # Return original text on error
# #         return bullet_text, 0, 0
# #
# #
# # def enhance_project_bullet_gemini(bullet_text, project_title, project_name, project_summary="",
# #                                   enhancement_type="general"):
# #     """
# #     Enhance a project bullet point using Google's Gemini model.
# #
# #     Args:
# #         bullet_text (str): The original bullet point text
# #         project_title (str): The job title of the user
# #         project_name (str): The name of the project
# #         project_summary (str): Optional summary of the project
# #         enhancement_type (str): Type of enhancement ('general' or 'ats')
# #
# #     Returns:
# #         tuple: (enhanced_text, input_tokens, output_tokens)
# #     """
# #     if not genai_api_key:
# #         return bullet_text, 0, 0
# #
# #     try:
# #         # Configure the model
# #         model = genai.GenerativeModel('gemini-pro')
# #
# #         # Generate the prompt with project context
# #         prompt = get_project_enhancement_prompt(
# #             bullet_text,
# #             project_title,
# #             project_name,
# #             project_summary,
# #             enhancement_type
# #         )
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
# #         # Return original text on error
# #         return bullet_text, 0, 0