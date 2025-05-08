# services/project_enhancement_service.py

import time
import openai
import google.generativeai as genai
from django.conf import settings
from job_portal.models import APIUsage

# Initialize APIs if keys are available
openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
genai_api_key = getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
if genai_api_key:
    genai.configure(api_key=genai_api_key)

# System message for AI
PROJECT_ENHANCEMENT_SYSTEM_MESSAGE = """You are an expert resume writer specializing in optimizing project descriptions 
for job applications. Your task is to enhance bullet points to be impactful, 
keyword-rich, and focused on measurable achievements and technical skills."""


def get_project_enhancement_prompt(bullet_text, project_title, project_name, project_summary="",
                                   enhancement_type="general"):
    """
    Get the prompt for enhancing project bullet points.

    Args:
        bullet_text (str): The original bullet point text
        project_title (str): The job title of the user
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
    if project_title:
        project_context += f"Role/Title: {project_title}\n"

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
        project_title (str): The job title of the user
        project_name (str): The name of the project
        project_summary (str): Optional summary of the project
        enhancement_type (str): Type of enhancement ('general' or 'ats')

    Returns:
        tuple: (enhanced_text, input_tokens, output_tokens)
    """
    if not openai.api_key:
        return bullet_text, 0, 0

    try:
        # Generate the prompt with project context
        prompt = get_project_enhancement_prompt(
            bullet_text,
            project_title,
            project_name,
            project_summary,
            enhancement_type
        )

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
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
        print(f"OpenAI API error: {str(e)}")
        # Return original text on error
        return bullet_text, 0, 0


def enhance_project_bullet_gemini(bullet_text, project_title, project_name, project_summary="",
                                  enhancement_type="general"):
    """
    Enhance a project bullet point using Google's Gemini model.

    Args:
        bullet_text (str): The original bullet point text
        project_title (str): The job title of the user
        project_name (str): The name of the project
        project_summary (str): Optional summary of the project
        enhancement_type (str): Type of enhancement ('general' or 'ats')

    Returns:
        tuple: (enhanced_text, input_tokens, output_tokens)
    """
    if not genai_api_key:
        return bullet_text, 0, 0

    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-pro')

        # Generate the prompt with project context
        prompt = get_project_enhancement_prompt(
            bullet_text,
            project_title,
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
        print(f"Gemini API error: {str(e)}")
        # Return original text on error
        return bullet_text, 0, 0