# prompts.py


# Bullet Generation Prompt
BULLET_GENERATION_PROMPT = """Generate 4 professional resume bullet points for a {job_title} position at {employer}. 
Each bullet point should:
1. Start with a strong action verb
2. Include measurable achievements with specific numbers (%, $, etc.)
3. Be concise (100-150 characters optimal)
4. Focus on accomplishments rather than just responsibilities
5. Include relevant technical skills where appropriate

Format the response as a simple list with one bullet point per line. 
Do not include bullet markers, numbers, or any other formatting."""

# Bullet Enhancement Prompt
BULLET_ENHANCEMENT_PROMPT = """Enhance the following resume bullet point to be more impactful:

Original: {bullet_text}

Instructions:
1. Ensure it starts with a strong action verb
2. Add specific metrics and quantifiable results (numbers, percentages, dollars)
3. Focus on achievements rather than responsibilities
4. Keep it concise yet impactful (100-150 characters optimal)
5. Maintain professional language and clarity

Provide only the enhanced bullet point text with no additional commentary."""

# ATS Optimization Prompt
ATS_OPTIMIZATION_PROMPT = """Optimize the following resume bullet point for Applicant Tracking Systems (ATS):

Original bullet point: {bullet_text}

{job_description_section}

Instructions:
1. Include relevant keywords from the job description when available
2. Keep the strong action verb at the beginning
3. Maintain quantifiable achievements and metrics
4. Ensure it remains clear and readable for humans
5. Keep it concise yet impactful

Provide only the optimized bullet point text with no additional commentary."""

# System Role Messages
RESUME_WRITER_SYSTEM_MESSAGE = "You are a professional resume writer specializing in creating impactful bullet points that highlight achievements and skills."

ATS_EXPERT_SYSTEM_MESSAGE = "You are an expert in optimizing resumes for ATS systems while keeping them compelling for human readers."