# ai_services.py
import time
import random
import openai
import google.generativeai as genai
from django.conf import settings

# Initialize APIs if keys are available
openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
genai_api_key = getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
if genai_api_key:
    genai.configure(api_key=genai_api_key)

# Updated prompts with more ATS focus
RESUME_WRITER_SYSTEM_MESSAGE = """You are an expert resume writer specializing in ATS-optimized resumes. 
Your task is to create impactful bullet points that highlight achievements, incorporate relevant skills,
and use industry-specific keywords that will pass through Applicant Tracking Systems."""


# Enhanced prompt for bullet generation with more parameters and configurable bullet count
def get_bullet_generation_prompt(job_title, employer, target_job_title, skills, responsibilities=None, bullet_count=3):
    """
    Get prompt for generating bullet points with configurable count.
    """
    # Ensure bullet_count is between 1 and 5
    bullet_count = min(max(int(bullet_count), 1), 5)

    prompt = f"""Generate {bullet_count} professional resume bullet points for a {job_title} position at {employer} 
that would be highly effective for applying to a {target_job_title} position.

Incorporate these skills where relevant: {skills}

"""

    if responsibilities:
        prompt += f"""
Based on these responsibilities/achievements: {responsibilities}
"""

    prompt += f"""
Each bullet point should:
1. Start with a strong action verb
2. Include measurable achievements with specific numbers (%, $, etc.)
3. Be concise (100-150 characters optimal)
4. Focus on accomplishments rather than just responsibilities
5. Include keywords relevant to the target position
6. Be optimized for Applicant Tracking Systems (ATS)

Format the response as a simple list with one bullet point per line. 
Provide exactly {bullet_count} bullet points.
Do not include bullet markers, numbers, or any other formatting."""

    return prompt


# Enhanced bullet enhancement prompt
def get_bullet_enhancement_prompt(bullet_text, enhancement_type="general"):
    if enhancement_type == "ats":
        return f"""Optimize the following resume bullet point specifically for Applicant Tracking Systems (ATS):

Original: {bullet_text}

Instructions:
1. Ensure it includes industry-standard keywords that ATS systems typically scan for
2. Keep a strong action verb at the beginning
3. Maintain quantifiable achievements and metrics
4. Ensure it remains clear and readable for humans
5. Keep it concise yet impactful (100-150 characters optimal)
6. Do not add any fictional achievements or details

Provide only the optimized bullet point text with no additional commentary."""

    else:  # general enhancement
        return f"""Enhance the following resume bullet point to be more impactful:

Original: {bullet_text}

Instructions:
1. Ensure it starts with a strong action verb
2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
3. Focus on achievements rather than responsibilities
4. Keep it concise yet impactful (100-150 characters optimal)
5. Maintain professional language and clarity
6. Do not add any fictional achievements or details

Provide only the enhanced bullet point text with no additional commentary."""


# ATS optimization prompt with job description
def get_ats_optimization_prompt(bullet_text, job_description=''):
    prompt = f"""Optimize the following resume bullet point for Applicant Tracking Systems (ATS):

Original bullet point: {bullet_text}

"""

    if job_description:
        prompt += f"""Target Job Description:
{job_description}

"""

    prompt += """Instructions:
1. Include relevant keywords from the job description when available
2. Keep the strong action verb at the beginning
3. Maintain quantifiable achievements and metrics
4. Ensure it remains clear and readable for humans
5. Keep it concise yet impactful
6. Do not add any fictional achievements or details

Provide only the optimized bullet point text with no additional commentary."""

    return prompt
def generate_bullets_chatgpt(job_title, employer, target_job_title=None, skills=None, responsibilities=None, bullet_count=3):
    """
    Generate bullet points using OpenAI's GPT models with enhanced parameters and customizable count.
    Returns the bullet points and token counts.
    """
    if not openai.api_key:
        return get_template_bullets(job_title, employer, bullet_count), 0, 0

    try:
        # Use target job title if provided, otherwise use current job title
        target = target_job_title if target_job_title else job_title
        skills_text = skills if skills else "relevant technical and soft skills"

        # Format the prompt with all details including bullet count
        prompt = get_bullet_generation_prompt(
            job_title=job_title,
            employer=employer,
            target_job_title=target,
            skills=skills_text,
            responsibilities=responsibilities,
            bullet_count=bullet_count
        )

        # Call OpenAI API with new client syntax
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # You can change this to gpt-4 if available
            messages=[
                {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7,
        )

        # Extract bullet points from response (updated method)
        content = response.choices[0].message.content.strip()
        bullets = [line.strip() for line in content.split('\n') if line.strip()]

        # Get token usage for cost calculation (updated method)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # Ensure we have exactly the requested number of bullet points
        requested_count = min(max(int(bullet_count), 1), 5)  # Between 1 and 5
        if len(bullets) < requested_count:
            # Add template bullets if needed
            template_bullets = get_template_bullets(job_title, employer)
            bullets.extend(template_bullets[:(requested_count - len(bullets))])
        elif len(bullets) > requested_count:
            bullets = bullets[:requested_count]

        return bullets, input_tokens, output_tokens

    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback to template bullets
        return get_template_bullets(job_title, employer, bullet_count), 0, 0


def enhance_bullet_chatgpt(bullet_text, enhancement_type="general", job_description=""):
    """
    Enhance a bullet point using OpenAI's GPT models with enhancement type.
    Returns the enhanced text and token counts.
    """
    if not openai.api_key:
        return enhance_bullet_basic(bullet_text), 0, 0

    try:
        # Choose prompt based on enhancement type
        if enhancement_type == "ats" and job_description:
            prompt = get_ats_optimization_prompt(bullet_text, job_description)
        else:
            prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)

        # Call OpenAI API with new client syntax
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )

        # Extract enhanced text from response (updated method)
        enhanced_text = response.choices[0].message.content.strip()

        # Get token usage for cost calculation (updated method)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        return enhanced_text, input_tokens, output_tokens

    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback to basic enhancement
        return enhance_bullet_basic(bullet_text), 0, 0

def generate_bullets_gemini(job_title, employer, target_job_title=None, skills=None, responsibilities=None, bullet_count=3):
    """
    Generate bullet points using Google's Gemini model with enhanced parameters and customizable count.
    Returns the bullet points and token counts.
    """
    if not genai_api_key:
        return get_template_bullets(job_title, employer, bullet_count), 0, 0

    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-pro')

        # Use target job title if provided, otherwise use current job title
        target = target_job_title if target_job_title else job_title
        skills_text = skills if skills else "relevant technical and soft skills"

        # Format the prompt with all details including bullet count
        prompt = get_bullet_generation_prompt(
            job_title=job_title,
            employer=employer,
            target_job_title=target,
            skills=skills_text,
            responsibilities=responsibilities,
            bullet_count=bullet_count
        )

        # Call Gemini API
        response = model.generate_content(prompt)

        # Extract bullet points from response
        content = response.text.strip()
        bullets = [line.strip() for line in content.split('\n') if line.strip()]

        # Gemini doesn't provide token counts directly, so we estimate
        # A very rough estimation: 1 token ≈ 4 characters
        input_chars = len(prompt)
        output_chars = len(content)
        input_tokens = input_chars // 4
        output_tokens = output_chars // 4

        # Ensure we have exactly the requested number of bullet points
        requested_count = min(max(int(bullet_count), 1), 5)  # Between 1 and 5
        if len(bullets) < requested_count:
            # Add template bullets if needed
            template_bullets = get_template_bullets(job_title, employer)
            bullets.extend(template_bullets[:(requested_count - len(bullets))])
        elif len(bullets) > requested_count:
            bullets = bullets[:requested_count]

        return bullets, input_tokens, output_tokens

    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        # Fallback to template bullets
        return get_template_bullets(job_title, employer, bullet_count), 0, 0


def enhance_bullet_gemini(bullet_text, enhancement_type="general", job_description=""):
    """
    Enhance a bullet point using Google's Gemini model with enhancement type.
    Returns the enhanced text and token counts.
    """
    if not genai_api_key:
        return enhance_bullet_basic(bullet_text), 0, 0

    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-pro')

        # Choose prompt based on enhancement type
        if enhancement_type == "ats" and job_description:
            prompt = get_ats_optimization_prompt(bullet_text, job_description)
        else:
            prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)

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
        # Fallback to basic enhancement
        return enhance_bullet_basic(bullet_text), 0, 0
def ats_optimize_chatgpt(bullet_text, job_description):
    """
    Optimize a bullet point for ATS systems using OpenAI.
    Returns the optimized text and token counts.
    """
    # This is essentially a specialized version of enhance_bullet_chatgpt
    return enhance_bullet_chatgpt(bullet_text, "ats", job_description)


def ats_optimize_gemini(bullet_text, job_description):
    """
    Optimize a bullet point for ATS systems using Gemini.
    Returns the optimized text and token counts.
    """
    # This is essentially a specialized version of enhance_bullet_gemini
    return enhance_bullet_gemini(bullet_text, "ats", job_description)


# Basic enhancement without AI APIs
def enhance_bullet_basic(bullet_text):
    """Helper function for basic bullet enhancement without API calls"""
    # Example enhancements
    enhancements = [
        lambda t: t.replace("improved", "significantly improved"),
        lambda t: t.replace("increased", "substantially increased"),
        lambda t: t.replace("reduced", "dramatically reduced"),
        lambda t: t.replace("managed", "successfully managed"),
        lambda t: t.replace("developed", "designed and developed"),
        lambda t: t + " resulting in significant cost savings" if "cost" not in t.lower() else t,
        lambda t: t + " within strict timeline constraints" if "time" not in t.lower() else t,
        lambda t: t.replace("team", "cross-functional team"),
    ]

    # Apply a random enhancement
    enhanced_text = bullet_text

    # Apply quantitative metrics if none present
    if not any(c.isdigit() for c in enhanced_text):
        metrics = ["20%", "30%", "25%", "40%", "$50K", "15%"]
        improvement_phrases = [
            f" resulting in {random.choice(metrics)} improvement in efficiency",
            f" leading to {random.choice(metrics)} increase in productivity",
            f" generating {random.choice(metrics)} in cost savings",
            f" improving customer satisfaction by {random.choice(metrics)}"
        ]
        enhanced_text += random.choice(improvement_phrases)

    # Apply action verb enhancement if needed
    action_verbs = ["Developed", "Implemented", "Streamlined", "Spearheaded",
                    "Managed", "Executed", "Coordinated", "Led"]

    if not any(verb.lower() in enhanced_text.lower()[:15] for verb in action_verbs):
        enhanced_text = f"{random.choice(action_verbs)} {enhanced_text[0].lower()}{enhanced_text[1:]}"

    # Apply a random generic enhancement
    for _ in range(2):  # Apply up to 2 enhancements
        enhancement = random.choice(enhancements)
        new_text = enhancement(enhanced_text)
        if new_text != enhanced_text:  # Only keep if it actually changed something
            enhanced_text = new_text
            break

    return enhanced_text


# Template-based bullets for fallback with configurable count
def get_template_bullets(job_title, employer, count=3):
    """
    Helper function to get template bullets based on job title with configurable count.
    Count will be between 1 and 5.
    """
    # Ensure count is between 1 and 5
    count = min(max(int(count), 1), 5)

    job_bullets = {
        'software engineer': [
            f"Developed scalable web applications using Python and Django at {employer}, reducing page load times by 45%",
            f"Led implementation of CI/CD pipeline at {employer}, decreasing deployment time by 60% and reducing bugs in production by 35%",
            f"Optimized database queries for {employer}'s customer portal, resulting in 50% improvement in API response times",
            f"Collaborated with cross-functional teams to redesign {employer}'s authentication system, enhancing security while maintaining user experience",
            f"Implemented automated testing strategies at {employer}, increasing code coverage by 70% and reducing regression bugs by 40%"
        ],
        'data scientist': [
            f"Analyzed customer data using Python and SQL at {employer}, identifying patterns that increased sales by 28%",
            f"Built machine learning models that improved {employer}'s sales forecast accuracy by 40%, directly impacting inventory management",
            f"Created interactive dashboards using Tableau for {employer}'s executives, enabling data-driven decisions that reduced costs by $150K annually",
            f"Implemented A/B testing framework for {employer}'s marketing campaigns, increasing conversion rates by 35%",
            f"Developed NLP algorithms to analyze customer feedback at {employer}, improving product satisfaction scores by 25%"
        ],
        'project manager': [
            f"Led cross-functional teams of 12+ members at {employer}, delivering 5 critical projects on time and under budget",
            f"Implemented Agile methodology at {employer}, increasing team productivity by 30% and reducing time-to-market",
            f"Managed $1.2M budget for {employer}'s digital transformation initiative, achieving all KPIs while 15% under budget",
            f"Developed comprehensive project plans for {employer} that reduced scope creep by 40% and improved stakeholder satisfaction",
            f"Streamlined communication processes at {employer}, reducing meeting time by 25% while improving information flow across departments"
        ],
        'marketing manager': [
            f"Developed and executed marketing strategies that increased {employer}'s brand awareness by 45% in key markets",
            f"Managed {employer}'s $800K digital marketing budget, achieving 135% of lead generation targets within first 6 months",
            f"Launched social media campaigns for {employer} that grew follower base by 75% and engagement by 82%",
            f"Conducted market research for {employer}, identifying opportunities that resulted in two product launches generating $2.5M in first-year revenue",
            f"Optimized {employer}'s SEO strategy, increasing organic traffic by 65% and reducing cost-per-acquisition by 30%"
        ],
        'frontend developer': [
            f"Developed responsive user interfaces for {employer}'s flagship product using React and TypeScript, increasing user engagement by 38%",
            f"Improved web performance at {employer} by implementing code splitting and lazy loading, reducing initial load time by 45%",
            f"Collaborated with UX designers to implement intuitive interfaces at {employer}, leading to a 27% improvement in user retention",
            f"Refactored legacy codebase at {employer} to modern standards, reducing bundle size by 35% and improving maintainability",
            f"Implemented comprehensive UI testing suite for {employer}, decreasing visual regression issues by 60%"
        ],
        'backend developer': [
            f"Designed and implemented RESTful APIs for {employer}'s platform, handling 500K+ daily requests with 99.9% uptime",
            f"Optimized database architecture at {employer}, reducing query times by 65% and improving system scalability",
            f"Implemented microservices architecture at {employer}, enabling 3x faster feature deployment and improved system resilience",
            f"Developed authentication and authorization system for {employer}, enhancing security while maintaining excellent user experience",
            f"Created automated data processing pipelines at {employer}, reducing manual work by 80% and ensuring data integrity"
        ],
        'data analyst': [
            f"Analyzed customer behavior data at {employer}, identifying patterns that led to a 32% increase in customer retention",
            f"Created automated reporting dashboards for {employer}, saving 15+ hours weekly and improving data visibility across departments",
            f"Conducted in-depth market analysis for {employer}, informing strategic decisions that increased quarterly revenue by 18%",
            f"Implemented improved data collection methods at {employer}, increasing data accuracy by 45% and reducing missing data points",
            f"Developed statistical models for {employer} that predicted customer churn with 85% accuracy, enabling proactive retention measures"
        ],
        'product manager': [
            f"Led development of key product features at {employer}, increasing user adoption by 40% and reducing churn by 25%",
            f"Conducted comprehensive market analysis for {employer}, identifying unmet customer needs that led to 3 successful product launches",
            f"Created and managed product roadmap at {employer}, aligning stakeholder expectations and delivering all milestones on schedule",
            f"Implemented customer feedback loops at {employer}, resulting in 35% higher customer satisfaction and improved product-market fit",
            f"Coordinated cross-functional team of 15 members at {employer}, streamlining product development lifecycle by 30%"
        ]
    }

    # Normalize job title for matching
    job_title_lower = job_title.lower()

    # Get the appropriate bullet points based on job title or use generic ones
    job_key = next((key for key in job_bullets if key in job_title_lower), None)

    if job_key:
        return job_bullets[job_key][:count]
    else:
        # Generic bullet points for any job
        generic_bullets = [
            f"Spearheaded key initiatives at {employer} that improved operational efficiency by 20% and reduced annual costs by $45K",
            f"Collaborated with cross-functional teams at {employer} to implement best practices and streamline workflows, increasing productivity by 25%",
            f"Managed multiple projects simultaneously at {employer}, meeting 100% of deadlines while maintaining exceptional quality standards",
            f"Recognized for outstanding performance at {employer}, receiving commendation from senior leadership for contributions to company growth",
            f"Implemented innovative solutions at {employer} that resolved critical business challenges and improved customer satisfaction by 30%"
        ]
        return generic_bullets[:count]


# # ai_services.py
# import time
# import random
# import openai
# import google.generativeai as genai
# from django.conf import settings
#
# # Initialize APIs if keys are available
# openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
# genai_api_key = getattr(settings, 'GOOGLE_GENAI_API_KEY', None)
# if genai_api_key:
#     genai.configure(api_key=genai_api_key)
#
# # Updated prompts with more ATS focus
# RESUME_WRITER_SYSTEM_MESSAGE = """You are an expert resume writer specializing in ATS-optimized resumes.
# Your task is to create impactful bullet points that highlight achievements, incorporate relevant skills,
# and use industry-specific keywords that will pass through Applicant Tracking Systems."""
#
#
# # Enhanced prompt for bullet generation with more parameters
# def get_bullet_generation_prompt(job_title, employer, target_job_title, skills, responsibilities=None):
#     prompt = f"""Generate 4 professional resume bullet points for a {job_title} position at {employer}
# that would be highly effective for applying to a {target_job_title} position.
#
# Incorporate these skills where relevant: {skills}
#
# """
#
#     if responsibilities:
#         prompt += f"""
# Based on these responsibilities/achievements: {responsibilities}
# """
#
#     prompt += """
# Each bullet point should:
# 1. Start with a strong action verb
# 2. Include measurable achievements with specific numbers (%, $, etc.)
# 3. Be concise (100-150 characters optimal)
# 4. Focus on accomplishments rather than just responsibilities
# 5. Include keywords relevant to the target position
# 6. Be optimized for Applicant Tracking Systems (ATS)
#
# Format the response as a simple list with one bullet point per line.
# Do not include bullet markers, numbers, or any other formatting."""
#
#     return prompt
#
#
# # Enhanced bullet enhancement prompt
# def get_bullet_enhancement_prompt(bullet_text, enhancement_type="general"):
#     if enhancement_type == "ats":
#         return f"""Optimize the following resume bullet point specifically for Applicant Tracking Systems (ATS):
#
# Original: {bullet_text}
#
# Instructions:
# 1. Ensure it includes industry-standard keywords that ATS systems typically scan for
# 2. Keep a strong action verb at the beginning
# 3. Maintain quantifiable achievements and metrics
# 4. Ensure it remains clear and readable for humans
# 5. Keep it concise yet impactful (100-150 characters optimal)
# 6. Do not add any fictional achievements or details
#
# Provide only the optimized bullet point text with no additional commentary."""
#
#     else:  # general enhancement
#         return f"""Enhance the following resume bullet point to be more impactful:
#
# Original: {bullet_text}
#
# Instructions:
# 1. Ensure it starts with a strong action verb
# 2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
# 3. Focus on achievements rather than responsibilities
# 4. Keep it concise yet impactful (100-150 characters optimal)
# 5. Maintain professional language and clarity
# 6. Do not add any fictional achievements or details
#
# Provide only the enhanced bullet point text with no additional commentary."""
#
#
# # ATS optimization prompt with job description
# def get_ats_optimization_prompt(bullet_text, job_description=''):
#     prompt = f"""Optimize the following resume bullet point for Applicant Tracking Systems (ATS):
#
# Original bullet point: {bullet_text}
#
# """
#
#     if job_description:
#         prompt += f"""Target Job Description:
# {job_description}
#
# """
#
#     prompt += """Instructions:
# 1. Include relevant keywords from the job description when available
# 2. Keep the strong action verb at the beginning
# 3. Maintain quantifiable achievements and metrics
# 4. Ensure it remains clear and readable for humans
# 5. Keep it concise yet impactful
# 6. Do not add any fictional achievements or details
#
# Provide only the optimized bullet point text with no additional commentary."""
#
#     return prompt
#
# #
# # # ChatGPT Service Functions
# # def generate_bullets_chatgpt(job_title, employer, target_job_title=None, skills=None, responsibilities=None):
# #     """
# #     Generate bullet points using OpenAI's GPT models with enhanced parameters.
# #     Returns the bullet points and token counts.
# #     """
# #     if not openai.api_key:
# #         return get_template_bullets(job_title, employer), 0, 0
# #
# #     try:
# #         # Use target job title if provided, otherwise use current job title
# #         target = target_job_title if target_job_title else job_title
# #         skills_text = skills if skills else "relevant technical and soft skills"
# #
# #         # Format the prompt with all details
# #         prompt = get_bullet_generation_prompt(
# #             job_title=job_title,
# #             employer=employer,
# #             target_job_title=target,
# #             skills=skills_text,
# #             responsibilities=responsibilities
# #         )
# #
# #         # Call OpenAI API
# #         response = openai.ChatCompletion.create(
# #             model="gpt-3.5-turbo",  # You can change this to gpt-4 if available
# #             messages=[
# #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# #                 {"role": "user", "content": prompt}
# #             ],
# #             max_tokens=600,
# #             temperature=0.7,
# #         )
# #
# #         # Extract bullet points from response
# #         content = response.choices[0].message.content.strip()
# #         bullets = [line.strip() for line in content.split('\n') if line.strip()]
# #
# #         # Get token usage for cost calculation
# #         input_tokens = response.usage.prompt_tokens
# #         output_tokens = response.usage.completion_tokens
# #
# #         # Ensure we have exactly 4 bullet points
# #         if len(bullets) < 4:
# #             # Add template bullets if needed
# #             template_bullets = get_template_bullets(job_title, employer)
# #             bullets.extend(template_bullets[:(4 - len(bullets))])
# #         elif len(bullets) > 4:
# #             bullets = bullets[:4]
# #
# #         return bullets, input_tokens, output_tokens
# #
# #     except Exception as e:
# #         print(f"OpenAI API error: {str(e)}")
# #         # Fallback to template bullets
# #         return get_template_bullets(job_title, employer), 0, 0
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
# #         # Call OpenAI API
# #         response = openai.ChatCompletion.create(
# #             model="gpt-3.5-turbo",
# #             messages=[
# #                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
# #                 {"role": "user", "content": prompt}
# #             ],
# #             max_tokens=150,
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
# #         # Fallback to basic enhancement
# #         return enhance_bullet_basic(bullet_text), 0, 0
#
# def generate_bullets_chatgpt(job_title, employer, target_job_title=None, skills=None, responsibilities=None):
#     """
#     Generate bullet points using OpenAI's GPT models with enhanced parameters.
#     Returns the bullet points and token counts.
#     """
#     if not openai.api_key:
#         return get_template_bullets(job_title, employer), 0, 0
#
#     try:
#         # Use target job title if provided, otherwise use current job title
#         target = target_job_title if target_job_title else job_title
#         skills_text = skills if skills else "relevant technical and soft skills"
#
#         # Format the prompt with all details
#         prompt = get_bullet_generation_prompt(
#             job_title=job_title,
#             employer=employer,
#             target_job_title=target,
#             skills=skills_text,
#             responsibilities=responsibilities
#         )
#
#         # Call OpenAI API with new client syntax
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",  # You can change this to gpt-4 if available
#             messages=[
#                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=600,
#             temperature=0.7,
#         )
#
#         # Extract bullet points from response (updated method)
#         content = response.choices[0].message.content.strip()
#         bullets = [line.strip() for line in content.split('\n') if line.strip()]
#
#         # Get token usage for cost calculation (updated method)
#         input_tokens = response.usage.prompt_tokens
#         output_tokens = response.usage.completion_tokens
#
#         # Ensure we have exactly 4 bullet points
#         if len(bullets) < 4:
#             # Add template bullets if needed
#             template_bullets = get_template_bullets(job_title, employer)
#             bullets.extend(template_bullets[:(4 - len(bullets))])
#         elif len(bullets) > 4:
#             bullets = bullets[:4]
#
#         return bullets, input_tokens, output_tokens
#
#     except Exception as e:
#         print(f"OpenAI API error: {str(e)}")
#         # Fallback to template bullets
#         return get_template_bullets(job_title, employer), 0, 0
#
#
# def enhance_bullet_chatgpt(bullet_text, enhancement_type="general", job_description=""):
#     """
#     Enhance a bullet point using OpenAI's GPT models with enhancement type.
#     Returns the enhanced text and token counts.
#     """
#     if not openai.api_key:
#         return enhance_bullet_basic(bullet_text), 0, 0
#
#     try:
#         # Choose prompt based on enhancement type
#         if enhancement_type == "ats" and job_description:
#             prompt = get_ats_optimization_prompt(bullet_text, job_description)
#         else:
#             prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)
#
#         # Call OpenAI API with new client syntax
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": RESUME_WRITER_SYSTEM_MESSAGE},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=150,
#             temperature=0.7,
#         )
#
#         # Extract enhanced text from response (updated method)
#         enhanced_text = response.choices[0].message.content.strip()
#
#         # Get token usage for cost calculation (updated method)
#         input_tokens = response.usage.prompt_tokens
#         output_tokens = response.usage.completion_tokens
#
#         return enhanced_text, input_tokens, output_tokens
#
#     except Exception as e:
#         print(f"OpenAI API error: {str(e)}")
#         # Fallback to basic enhancement
#         return enhance_bullet_basic(bullet_text), 0, 0
#
#
# # Gemini Service Functions
# def generate_bullets_gemini(job_title, employer, target_job_title=None, skills=None, responsibilities=None):
#     """
#     Generate bullet points using Google's Gemini model with enhanced parameters.
#     Returns the bullet points and token counts.
#     """
#     if not genai_api_key:
#         return get_template_bullets(job_title, employer), 0, 0
#
#     try:
#         # Configure the model
#         model = genai.GenerativeModel('gemini-pro')
#
#         # Use target job title if provided, otherwise use current job title
#         target = target_job_title if target_job_title else job_title
#         skills_text = skills if skills else "relevant technical and soft skills"
#
#         # Format the prompt with all details
#         prompt = get_bullet_generation_prompt(
#             job_title=job_title,
#             employer=employer,
#             target_job_title=target,
#             skills=skills_text,
#             responsibilities=responsibilities
#         )
#
#         # Call Gemini API
#         response = model.generate_content(prompt)
#
#         # Extract bullet points from response
#         content = response.text.strip()
#         bullets = [line.strip() for line in content.split('\n') if line.strip()]
#
#         # Gemini doesn't provide token counts directly, so we estimate
#         # A very rough estimation: 1 token ≈ 4 characters
#         input_chars = len(prompt)
#         output_chars = len(content)
#         input_tokens = input_chars // 4
#         output_tokens = output_chars // 4
#
#         # Ensure we have exactly 4 bullet points
#         if len(bullets) < 4:
#             # Add template bullets if needed
#             template_bullets = get_template_bullets(job_title, employer)
#             bullets.extend(template_bullets[:(4 - len(bullets))])
#         elif len(bullets) > 4:
#             bullets = bullets[:4]
#
#         return bullets, input_tokens, output_tokens
#
#     except Exception as e:
#         print(f"Gemini API error: {str(e)}")
#         # Fallback to template bullets
#         return get_template_bullets(job_title, employer), 0, 0
#
#
# def enhance_bullet_gemini(bullet_text, enhancement_type="general", job_description=""):
#     """
#     Enhance a bullet point using Google's Gemini model with enhancement type.
#     Returns the enhanced text and token counts.
#     """
#     if not genai_api_key:
#         return enhance_bullet_basic(bullet_text), 0, 0
#
#     try:
#         # Configure the model
#         model = genai.GenerativeModel('gemini-pro')
#
#         # Choose prompt based on enhancement type
#         if enhancement_type == "ats" and job_description:
#             prompt = get_ats_optimization_prompt(bullet_text, job_description)
#         else:
#             prompt = get_bullet_enhancement_prompt(bullet_text, enhancement_type)
#
#         # Call Gemini API
#         response = model.generate_content(prompt)
#
#         # Extract enhanced text from response
#         enhanced_text = response.text.strip()
#
#         # Gemini doesn't provide token counts directly, so we estimate
#         # A very rough estimation: 1 token ≈ 4 characters
#         input_chars = len(prompt)
#         output_chars = len(enhanced_text)
#         input_tokens = input_chars // 4
#         output_tokens = output_chars // 4
#
#         return enhanced_text, input_tokens, output_tokens
#
#     except Exception as e:
#         print(f"Gemini API error: {str(e)}")
#         # Fallback to basic enhancement
#         return enhance_bullet_basic(bullet_text), 0, 0
#
#
# def ats_optimize_chatgpt(bullet_text, job_description):
#     """
#     Optimize a bullet point for ATS systems using OpenAI.
#     Returns the optimized text and token counts.
#     """
#     # This is essentially a specialized version of enhance_bullet_chatgpt
#     return enhance_bullet_chatgpt(bullet_text, "ats", job_description)
#
#
# def ats_optimize_gemini(bullet_text, job_description):
#     """
#     Optimize a bullet point for ATS systems using Gemini.
#     Returns the optimized text and token counts.
#     """
#     # This is essentially a specialized version of enhance_bullet_gemini
#     return enhance_bullet_gemini(bullet_text, "ats", job_description)
#
#
# # Basic enhancement without AI APIs
# def enhance_bullet_basic(bullet_text):
#     """Helper function for basic bullet enhancement without API calls"""
#     # Example enhancements
#     enhancements = [
#         lambda t: t.replace("improved", "significantly improved"),
#         lambda t: t.replace("increased", "substantially increased"),
#         lambda t: t.replace("reduced", "dramatically reduced"),
#         lambda t: t.replace("managed", "successfully managed"),
#         lambda t: t.replace("developed", "designed and developed"),
#         lambda t: t + " resulting in significant cost savings" if "cost" not in t.lower() else t,
#         lambda t: t + " within strict timeline constraints" if "time" not in t.lower() else t,
#         lambda t: t.replace("team", "cross-functional team"),
#     ]
#
#     # Apply a random enhancement
#     enhanced_text = bullet_text
#
#     # Apply quantitative metrics if none present
#     if not any(c.isdigit() for c in enhanced_text):
#         metrics = ["20%", "30%", "25%", "40%", "$50K", "15%"]
#         improvement_phrases = [
#             f" resulting in {random.choice(metrics)} improvement in efficiency",
#             f" leading to {random.choice(metrics)} increase in productivity",
#             f" generating {random.choice(metrics)} in cost savings",
#             f" improving customer satisfaction by {random.choice(metrics)}"
#         ]
#         enhanced_text += random.choice(improvement_phrases)
#
#     # Apply action verb enhancement if needed
#     action_verbs = ["Developed", "Implemented", "Streamlined", "Spearheaded",
#                     "Managed", "Executed", "Coordinated", "Led"]
#
#     if not any(verb.lower() in enhanced_text.lower()[:15] for verb in action_verbs):
#         enhanced_text = f"{random.choice(action_verbs)} {enhanced_text[0].lower()}{enhanced_text[1:]}"
#
#     # Apply a random generic enhancement
#     for _ in range(2):  # Apply up to 2 enhancements
#         enhancement = random.choice(enhancements)
#         new_text = enhancement(enhanced_text)
#         if new_text != enhanced_text:  # Only keep if it actually changed something
#             enhanced_text = new_text
#             break
#
#     return enhanced_text
#
#
# # Template-based bullets for fallback
# def get_template_bullets(job_title, employer):
#     """Helper function to get template bullets based on job title"""
#     job_bullets = {
#         'software engineer': [
#             f"Developed scalable web applications using Python and Django at {employer}, reducing page load times by 45%",
#             f"Led implementation of CI/CD pipeline at {employer}, decreasing deployment time by 60% and reducing bugs in production by 35%",
#             f"Optimized database queries for {employer}'s customer portal, resulting in 50% improvement in API response times",
#             f"Collaborated with cross-functional teams to redesign {employer}'s authentication system, enhancing security while maintaining user experience"
#         ],
#         'data scientist': [
#             f"Analyzed customer data using Python and SQL at {employer}, identifying patterns that increased sales by 28%",
#             f"Built machine learning models that improved {employer}'s sales forecast accuracy by 40%, directly impacting inventory management",
#             f"Created interactive dashboards using Tableau for {employer}'s executives, enabling data-driven decisions that reduced costs by $150K annually",
#             f"Implemented A/B testing framework for {employer}'s marketing campaigns, increasing conversion rates by 35%"
#         ],
#         'project manager': [
#             f"Led cross-functional teams of 12+ members at {employer}, delivering 5 critical projects on time and under budget",
#             f"Implemented Agile methodology at {employer}, increasing team productivity by 30% and reducing time-to-market",
#             f"Managed $1.2M budget for {employer}'s digital transformation initiative, achieving all KPIs while 15% under budget",
#             f"Developed comprehensive project plans for {employer} that reduced scope creep by 40% and improved stakeholder satisfaction"
#         ],
#         'marketing manager': [
#             f"Developed and executed marketing strategies that increased {employer}'s brand awareness by 45% in key markets",
#             f"Managed {employer}'s $800K digital marketing budget, achieving 135% of lead generation targets within first 6 months",
#             f"Launched social media campaigns for {employer} that grew follower base by 75% and engagement by 82%",
#             f"Conducted market research for {employer}, identifying opportunities that resulted in two product launches generating $2.5M in first-year revenue"
#         ]
#     }
#
#     # Normalize job title for matching
#     job_title_lower = job_title.lower()
#
#     # Get the appropriate bullet points based on job title or use generic ones
#     job_key = next((key for key in job_bullets if key in job_title_lower), None)
#
#     if job_key:
#         return job_bullets[job_key]
#     else:
#         # Generic bullet points for any job
#         return [
#             f"Spearheaded key initiatives at {employer} that improved operational efficiency by 20% and reduced annual costs by $45K",
#             f"Collaborated with cross-functional teams at {employer} to implement best practices and streamline workflows, increasing productivity by 25%",
#             f"Managed multiple projects simultaneously at {employer}, meeting 100% of deadlines while maintaining exceptional quality standards",
#             f"Recognized for outstanding performance at {employer}, receiving commendation from senior leadership for contributions to company growth"
#         ]