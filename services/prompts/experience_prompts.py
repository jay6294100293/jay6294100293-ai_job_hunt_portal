# services/ai_prompts/prompts.py

def get_dynamic_bullet_generation_prompt(job_title, employer=None, target_job_title=None, skills=None, responsibilities=None, bullet_count=3):
    """
    Get prompt for generating bullet points, making employer optional.
    """
    try:
        bullet_count = min(max(int(bullet_count), 1), 5) # Ensure valid range
    except ValueError:
        bullet_count = 3 # Default if conversion fails

    if employer and employer.strip():
        location_text = f"at {employer.strip()}"
    else:
        location_text = "for a relevant company" # Generic if no employer

    prompt_intro = f"Generate {bullet_count} professional resume bullet points for a {job_title} position {location_text}"

    if target_job_title and target_job_title.strip():
        prompt_intro += f" that would be highly effective for applying to a {target_job_title.strip()} position."
    else:
        prompt_intro += "." # End sentence if no target job title

    prompt_skills = ""
    if skills and skills.strip():
        prompt_skills = f"\nIncorporate these skills where relevant: {skills.strip()}"

    prompt_responsibilities = ""
    if responsibilities and responsibilities.strip():
        prompt_responsibilities = f"\nConsider these responsibilities/achievements: {responsibilities.strip()}"


    prompt_guidelines = """
Each bullet point should:
1. Start with a strong action verb.
2. Include measurable achievements with specific numbers (%, $, etc.) where possible.
3. Be concise (around 100-150 characters is optimal for many ATS, but can be up to 200-250 characters if detailed and impactful).
4. Focus on accomplishments rather than just responsibilities.
5. Be tailored and sound professional.

Format the response as a simple list with one bullet point per line.
Do not include bullet markers (like * or -), numbers, or any other formatting before each bullet point. Just the text of the bullet points, each on a new line."""

    return f"{prompt_intro}{prompt_skills}{prompt_responsibilities}\n{prompt_guidelines}"


# Original Bullet Generation Prompt (kept for reference or other uses)
# This one requires 'employer' to be formatted in.
BULLET_GENERATION_PROMPT_ORIGINAL_WITH_EMPLOYER = """Generate 4 professional resume bullet points for a {job_title} position at {employer}. 
Each bullet point should:
1. Start with a strong action verb
2. Include measurable achievements with specific numbers (%, $, etc.)
3. Be concise (100-150 characters optimal)
4. Focus on accomplishments rather than just responsibilities
5. Include relevant technical skills where appropriate

Format the response as a simple list with one bullet point per line. 
Do not include bullet markers, numbers, or any other formatting."""


# Updated Bullet Enhancement Prompt
BULLET_ENHANCEMENT_PROMPT = """Enhance the following resume bullet point to be more impactful:

Original: {bullet_text}

Instructions:
1. Ensure it starts with a strong action verb.
2. Add specific metrics and quantifiable results (numbers, percentages, dollars) if appropriate and not forced.
3. Focus on achievements rather than just responsibilities.
4. Keep it concise yet impactful (ideally 100-200 characters).
5. Maintain professional language and clarity.
6. If the original bullet is already strong, refine it subtly or state that it's well-crafted.

Provide exactly ONE enhanced bullet point as your complete response. Do not provide alternatives or multiple versions. If multiple approaches are possible, select the most impactful one."""

# ATS Optimization Prompt
ATS_OPTIMIZATION_PROMPT = """Optimize the following resume bullet point for Applicant Tracking Systems (ATS), considering the provided job description context if available:

Original bullet point: {bullet_text}

{job_description_section}

Instructions:
1. Include relevant keywords naturally from the job description (if provided). Do not keyword stuff.
2. Ensure the bullet starts with a strong action verb.
3. Maintain or enhance quantifiable achievements and metrics.
4. Ensure clarity and readability for human reviewers.
5. Keep it concise and impactful.
6. If the job description is not provided, optimize for general best practices for a {job_title} role.

Provide only the optimized bullet point text with no additional commentary."""

# System Role Messages
RESUME_WRITER_SYSTEM_MESSAGE = "You are an expert AI resume writer. Your goal is to help users create highly effective, professional, and achievement-oriented resume content that stands out to recruiters and hiring managers. Focus on clarity, impact, and conciseness."

ATS_EXPERT_SYSTEM_MESSAGE = "You are an AI assistant specializing in optimizing resume content for Applicant Tracking Systems (ATS) while ensuring the content remains compelling and readable for human reviewers. You understand how to incorporate keywords naturally and highlight relevant skills and achievements."


# # experience_prompts.py
#
#
# # Bullet Generation Prompt
# BULLET_GENERATION_PROMPT = """Generate 4 professional resume bullet points for a {job_title} position at {employer}.
# Each bullet point should:
# 1. Start with a strong action verb
# 2. Include measurable achievements with specific numbers (%, $, etc.)
# 3. Be concise (100-150 characters optimal)
# 4. Focus on accomplishments rather than just responsibilities
# 5. Include relevant technical skills where appropriate
#
# Format the response as a simple list with one bullet point per line.


# Do not include bullet markers, numbers, or any other formatting."""
#
# # Bullet Enhancement Prompt
# BULLET_ENHANCEMENT_PROMPT = """Enhance the following resume bullet point to be more impactful:
#
# Original: {bullet_text}
#
# Instructions:
# 1. Ensure it starts with a strong action verb
# 2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
# 3. Focus on achievements rather than responsibilities
# 4. Keep it concise yet impactful (100-150 characters optimal)
# 5. Maintain professional language and clarity
#
# Provide only the enhanced bullet point text with no additional commentary."""
#
# # ATS Optimization Prompt
# ATS_OPTIMIZATION_PROMPT = """Optimize the following resume bullet point for Applicant Tracking Systems (ATS):
#
# Original bullet point: {bullet_text}
#
# {job_description_section}
#
# Instructions:
# 1. Include relevant keywords from the job description when available
# 2. Keep the strong action verb at the beginning
# 3. Maintain quantifiable achievements and metrics
# 4. Ensure it remains clear and readable for humans
# 5. Keep it concise yet impactful
#
# Provide only the optimized bullet point text with no additional commentary."""
#
# # System Role Messages
# RESUME_WRITER_SYSTEM_MESSAGE = "You are a professional resume writer specializing in creating impactful bullet points that highlight achievements and skills."
#
# ATS_EXPERT_SYSTEM_MESSAGE = "You are an expert in optimizing resumes for ATS systems while keeping them compelling for human readers."