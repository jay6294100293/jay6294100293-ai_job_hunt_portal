import tempfile
import time

from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods

from ai_job_hunt_portal import settings
from job_portal.models import (
    Resume, Skill, Experience, ExperienceBulletPoint,
    Education, Certification, Project, ProjectBulletPoint,
    Language, CustomData, APIUsage, JobInput
)
from services.bullets_ai_services import generate_bullets_chatgpt, get_template_bullets, generate_bullets_gemini, \
    enhance_bullet_chatgpt, enhance_bullet_gemini, enhance_bullet_basic, ats_optimize_chatgpt, ats_optimize_gemini


@login_required
@require_http_methods(["POST"])
def save_section(request, resume_id):
    """
    Save a specific section of a resume that has been edited.
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    section = request.session.get('edit_section', '')
    form_data = request.session.get('resume_form_data', {})

    try:
        with transaction.atomic():
            # Update the appropriate section
            if section == 'personal':
                personal_info = form_data.get('personal_info', {})
                resume.first_name = personal_info.get('first_name', resume.first_name)
                resume.mid_name = personal_info.get('mid_name', resume.mid_name)
                resume.last_name = personal_info.get('last_name', resume.last_name)
                resume.email = personal_info.get('email', resume.email)
                resume.phone = personal_info.get('phone', resume.phone)
                resume.address = personal_info.get('address', resume.address)
                resume.linkedin = personal_info.get('linkedin', resume.linkedin)
                resume.github = personal_info.get('github', resume.github)
                resume.portfolio = personal_info.get('portfolio', resume.portfolio)
                resume.save()

            elif section == 'summary':
                summary = form_data.get('summary', '')
                if isinstance(summary, dict):
                    summary = summary.get('summary', '')
                resume.summary = summary
                resume.save()

            elif section == 'skills':
                # Clear existing skills
                resume.skills.all().delete()

                # Add new skills
                for skill_data in form_data.get('skills', []):
                    Skill.objects.create(
                        resume=resume,
                        skill_name=skill_data.get('skill_name', ''),
                        skill_type=skill_data.get('skill_type', 'technical'),
                        proficiency_level=skill_data.get('proficiency_level', 0)
                    )

            elif section == 'experience':
                # Clear existing experiences
                for exp in resume.experiences.all():
                    exp.bullet_points.all().delete()
                resume.experiences.all().delete()

                # Add new experiences
                for exp_data in form_data.get('experiences', []):
                    experience = Experience.objects.create(
                        resume=resume,
                        job_title=exp_data.get('job_title', ''),
                        employer=exp_data.get('employer', ''),
                        location=exp_data.get('location', ''),
                        start_date=exp_data.get('start_date') or None,
                        end_date=exp_data.get('end_date') if not exp_data.get('is_current', False) else None,
                        is_current=exp_data.get('is_current', False)
                    )

                    # Add bullet points
                    for bullet_data in exp_data.get('bullet_points', []):
                        bullet_text = bullet_data
                        # Handle both string and dict formats for bullet points
                        if isinstance(bullet_data, dict):
                            bullet_text = bullet_data.get('description', '')

                        if bullet_text:
                            ExperienceBulletPoint.objects.create(
                                experience=experience,
                                description=bullet_text
                            )

            elif section == 'education':
                # Clear existing education
                resume.educations.all().delete()

                # Add new education
                for edu_data in form_data.get('educations', []):
                    Education.objects.create(
                        resume=resume,
                        school_name=edu_data.get('school_name', ''),
                        location=edu_data.get('location', ''),
                        degree=edu_data.get('degree', ''),
                        degree_type=edu_data.get('degree_type', 'bachelor'),
                        field_of_study=edu_data.get('field_of_study', ''),
                        graduation_date=edu_data.get('graduation_date') or None,
                        gpa=edu_data.get('gpa') or None
                    )

            elif section == 'projects':
                # Clear existing projects
                for proj in resume.projects.all():
                    proj.bullet_points.all().delete()
                resume.projects.all().delete()

                # Add new projects
                for proj_data in form_data.get('projects', []):
                    project = Project.objects.create(
                        resume=resume,
                        project_name=proj_data.get('project_name', ''),
                        summary=proj_data.get('summary', ''),
                        start_date=proj_data.get('start_date') or None,
                        completion_date=proj_data.get('completion_date') or None,
                        project_link=proj_data.get('project_link', ''),
                        github_link=proj_data.get('github_link', '')
                    )

                    # Add bullet points
                    for bullet_text in proj_data.get('bullet_points', []):
                        if bullet_text:
                            ProjectBulletPoint.objects.create(
                                project=project,
                                description=bullet_text
                            )

            elif section == 'certifications':
                # Clear existing certifications
                resume.certifications.all().delete()

                # Add new certifications
                for cert_data in form_data.get('certifications', []):
                    Certification.objects.create(
                        resume=resume,
                        name=cert_data.get('name', ''),
                        institute=cert_data.get('institute', ''),
                        completion_date=cert_data.get('completion_date') or None,
                        expiration_date=cert_data.get('expiration_date') or None,
                        score=cert_data.get('score', ''),
                        link=cert_data.get('link', ''),
                        description=cert_data.get('description', '')
                    )

            elif section == 'languages':
                # Clear existing languages
                resume.languages.all().delete()

                # Add new languages
                for lang_data in form_data.get('languages', []):
                    Language.objects.create(
                        resume=resume,
                        language_name=lang_data.get('language_name', ''),
                        proficiency=lang_data.get('proficiency', 'basic')
                    )

            elif section == 'custom':
                # Clear existing custom sections
                resume.custom_data.all().delete()

                # Add new custom sections
                for custom_data in form_data.get('custom_sections', []):
                    if custom_data.get('name'):
                        CustomData.objects.create(
                            resume=resume,
                            name=custom_data.get('name', ''),
                            completion_date=custom_data.get('completion_date') or None,
                            bullet_points=custom_data.get('bullet_points', ''),
                            description=custom_data.get('description', ''),
                            link=custom_data.get('link', ''),
                            institution_name=custom_data.get('institution_name', '')
                        )

        # Clear session data
        if 'resume_form_data' in request.session:
            del request.session['resume_form_data']
        if 'edit_resume_id' in request.session:
            del request.session['edit_resume_id']
        if 'edit_section_only' in request.session:
            del request.session['edit_section_only']
        if 'edit_section' in request.session:
            del request.session['edit_section']

        messages.success(request, f"Resume {section} section updated successfully!")
        return redirect('job_portal:view_resume', resume_id=resume_id)

    except Exception as e:
        messages.error(request, f"Error updating resume section: {str(e)}")
        return redirect('job_portal:edit_resume_section', resume_id=resume_id, section=section)


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


@login_required
def get_ai_usage_stats(request):
    """
    Get AI usage statistics for the current user.
    Returns a JSON response with usage data.
    """
    # Get time period from request
    period = request.GET.get('period', 'month')  # 'day', 'week', 'month', 'all'

    # Calculate date filter based on period
    if period == 'day':
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = timezone.now() - timezone.timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now() - timezone.timedelta(days=30)
    else:  # 'all'
        start_date = None

    # Query API usage
    query = APIUsage.objects.filter(user=request.user)
    if start_date:
        query = query.filter(timestamp__gte=start_date)

    # Aggregate by API type
    chatgpt_usage = query.filter(api_name='chatgpt')
    gemini_usage = query.filter(api_name='gemini')

    # Calculate totals
    chatgpt_cost = sum([usage.cost for usage in chatgpt_usage])
    gemini_cost = sum([usage.cost for usage in gemini_usage])
    chatgpt_tokens = sum([usage.total_tokens for usage in chatgpt_usage])
    gemini_tokens = sum([usage.total_tokens for usage in gemini_usage])

    # Count operations
    operation_counts = {}
    for op in APIUsage.OPERATION_TYPES:
        op_code = op[0]
        operation_counts[op_code] = query.filter(operation=op_code).count()

    # Prepare response data
    data = {
        'period': period,
        'usage': {
            'chatgpt': {
                'cost': str(chatgpt_cost),
                'tokens': chatgpt_tokens,
                'count': chatgpt_usage.count()
            },
            'gemini': {
                'cost': str(gemini_cost),
                'tokens': gemini_tokens,
                'count': gemini_usage.count()
            }
        },
        'operations': operation_counts,
        'total_cost': str(chatgpt_cost + gemini_cost),
        'total_requests': query.count()
    }

    return JsonResponse(data)


@login_required
@require_http_methods(["GET"])
def htmx_add_form_row(request):
    """HTMX handler for adding a new form row dynamically."""
    form_type = request.GET.get('form_type')
    index = int(request.GET.get('index', 0))

    context = {'index': index}

    if form_type == 'skill':
        # Handle skill addition specifically
        skill_name = request.GET.get('skill_name', '')
        skill_type = request.GET.get('skill_type', '')
        proficiency = request.GET.get('proficiency', '50')
        years = request.GET.get('years', '')

        context.update({
            'skill_types': dict(Skill.SKILL_TYPES),
            'skill_name': skill_name,
            'skill_type': skill_type,
            'proficiency': proficiency,
            'years': years
        })

        # Return the skill card instead of a form row
        return render(request, 'resumes/partials/skill_form_row.html', context)
    elif form_type == 'experience':
        return render(request, 'resumes/partials/experience_form_row.html', context)
    elif form_type == 'education':
        context['degree_types'] = dict(Education.DEGREE_TYPES)
        return render(request, 'resumes/partials/education_form_row.html', context)
    elif form_type == 'project':
        return render(request, 'resumes/partials/project_form_row.html', context)
    elif form_type == 'certification':
        return render(request, 'resumes/partials/certification_form_row.html', context)
    elif form_type == 'language':
        context['proficiency_levels'] = dict(Language.PROFICIENCY_LEVELS)
        return render(request, 'resumes/partials/language_form_row.html', context)
    elif form_type == 'custom_section':
        return render(request, 'resumes/partials/custom_section_form_row.html', context)
    elif form_type == 'bullet_point':
        parent_index = request.GET.get('parent_index', 0)
        ai_engine = request.GET.get('ai_engine', 'chatgpt')  # Add AI engine parameter
        context.update({
            'parent_index': parent_index,
            'ai_engine': ai_engine  # Pass the AI engine to the template
        })
        return render(request, 'resumes/partials/bullet_point_form_row.html', context)

    return HttpResponse("Form type not recognized")


def preview_template(request, template_id):
    """
    Preview a resume template with comprehensive sample data that includes all model fields.
    Enhanced to support the fresh graduate template with appropriate sample data.
    """
    from django.shortcuts import render
    from django.http import HttpResponse

    # Check if we should use fresher resume data
    if template_id == 6:
        sample_resume = create_fresher_resume()
    else:
        sample_resume = create_experienced_resume()

    # For consistent template rendering, make sure the template exists
    try:
        # Render the template
        return render(request, f'resumes/templates/template{template_id}.html', {'resume': sample_resume})
    except Exception as e:
        # Return a basic error page with useful information
        error_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 30px;">
            <h1 style="color: #d32f2f;">Template Preview Error</h1>
            <p>There was a problem rendering the template:</p>
            <div style="background-color: #f8f8f8; padding: 15px; border-left: 5px solid #d32f2f; margin: 20px 0;">
                <code>{str(e)}</code>
            </div>
            <p>Please check that the template file exists at: <code>resumes/templates/template{template_id}.html</code></p>
            <p>Template ID: {template_id}</p>
        </div>
        """
        return HttpResponse(error_html)


def create_experienced_resume():
    """Create a sample resume for an experienced professional."""
    from datetime import date

    class DummyQuerySet(list):
        def exists(self):
            return len(self) > 0

        def all(self):
            return self

        def get_skill_type_display(self):
            return self.skill_type.capitalize() if hasattr(self, 'skill_type') else ""

    class DummyBulletPoint:
        def __init__(self, description):
            self.description = description
            self.keywords = DummyQuerySet()

    class DummyExperience:
        def __init__(self, job_title, employer, location, start_date, end_date=None, is_current=False):
            self.job_title = job_title
            self.employer = employer
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.is_current = is_current
            self.bullet_points = DummyQuerySet()

    class DummyEducation:
        def __init__(self, school_name, location, degree, field_of_study, degree_type, graduation_date, gpa=None,
                     start_date=None):
            self.school_name = school_name
            self.location = location
            self.degree = degree
            self.field_of_study = field_of_study
            self.degree_type = degree_type
            self.graduation_date = graduation_date
            self.start_date = start_date
            self.gpa = gpa
            self.achievements = "Dean's List: 2015-2017\nSenior Project: Advanced Machine Learning Application\nRecipient of Academic Excellence Scholarship"

    class DummySkill:
        def __init__(self, name, skill_type, proficiency_level):
            self.skill_name = name
            self.skill_type = skill_type
            self.proficiency_level = proficiency_level

        def get_skill_type_display(self):
            types = {
                'technical': 'Technical',
                'soft': 'Soft',
                'language': 'Language',
                'tool': 'Tool'
            }
            return types.get(self.skill_type, self.skill_type)

    class DummyProject:
        def __init__(self, name, summary, start_date, completion_date, project_link=None, github_link=None):
            self.project_name = name
            self.summary = summary
            self.start_date = start_date
            self.completion_date = completion_date
            self.project_link = project_link
            self.github_link = github_link
            self.bullet_points = DummyQuerySet()
            self.technologies = DummyQuerySet()

    class DummyCertification:
        def __init__(self, name, institute, completion_date, expiration_date=None, description=None, link=None,
                     score=None):
            self.name = name
            self.institute = institute
            self.completion_date = completion_date
            self.expiration_date = expiration_date
            self.description = description
            self.link = link
            self.score = score

    class DummyLanguage:
        def __init__(self, name, proficiency):
            self.language_name = name
            self.proficiency = proficiency

        def get_proficiency_display(self):
            return {"basic": "Basic", "intermediate": "Intermediate",
                    "advanced": "Advanced", "native": "Native"}[self.proficiency]

    class DummyCustomData:
        def __init__(self, name, completion_date=None, bullet_points=None, description=None, link=None,
                     institution_name=None):
            self.name = name
            self.completion_date = completion_date
            self.bullet_points = bullet_points
            self.description = description
            self.link = link
            self.institution_name = institution_name

    class DummyResume:
        def __init__(self):
            self.id = 1
            self.first_name = "Alex"
            self.mid_name = "J."
            self.last_name = "Morgan"
            self.full_name = "Alex J. Morgan"
            self.title = "Senior Full Stack Developer"
            self.email = "alex.morgan@example.com"
            self.phone = "(555) 123-4567"
            self.address = "123 Tech Avenue, Silicon Valley, CA 94123"
            self.linkedin = "https://linkedin.com/in/alexmorgan"
            self.github = "https://github.com/alexmorgan"
            self.portfolio = "https://alexmorgan.dev"
            self.summary = "Innovative full stack developer with 7+ years of experience building scalable web applications and leading development teams. Specialized in JavaScript, Python, and cloud technologies with a focus on performance optimization and user experience. Passionate about creating elegant solutions to complex problems and implementing best practices in software development."

            # Initialize collections as DummyQuerySet
            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.skills = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_data = DummyQuerySet()

    # Create a sample resume
    sample_resume = DummyResume()

    # Add experiences with more variety
    experiences = [
        DummyExperience(
            "Senior Software Engineer",
            "Tech Innovations Inc.",
            "San Francisco, CA",
            date(2020, 6, 1),
            None,  # end_date
            True  # is_current
        ),
        DummyExperience(
            "Lead Developer",
            "Digital Solutions Ltd.",
            "Seattle, WA",
            date(2018, 3, 1),
            date(2020, 5, 31),
            False
        ),
        DummyExperience(
            "Web Developer",
            "Creative Web Agency",
            "Portland, OR",
            date(2016, 1, 15),
            date(2018, 2, 28),
            False
        ),
    ]

    # Add bullet points to each experience
    experiences[0].bullet_points.extend([
        DummyBulletPoint(
            "Led a team of 7 developers to deliver a cloud-based enterprise solution that increased customer engagement by 45% and reduced operational costs by 30%"),
        DummyBulletPoint(
            "Implemented microservices architecture with Docker and Kubernetes that reduced deployment time by 60% and improved system scalability"),
        DummyBulletPoint(
            "Optimized database queries and implemented caching strategies resulting in a 40% improvement in application response time"),
        DummyBulletPoint(
            "Mentored junior developers through code reviews and pair programming sessions, improving team productivity by 25%")
    ])

    experiences[1].bullet_points.extend([
        DummyBulletPoint(
            "Designed and developed a customer portal using React and Node.js that increased user satisfaction by 35%"),
        DummyBulletPoint(
            "Implemented CI/CD pipelines with Jenkins, reducing integration issues by 50% and deployment failures by 70%"),
        DummyBulletPoint(
            "Led the migration from monolithic architecture to microservices, improving system reliability and reducing downtime by 80%")
    ])

    experiences[2].bullet_points.extend([
        DummyBulletPoint(
            "Developed responsive web applications using JavaScript, HTML5, and CSS3 for clients across various industries"),
        DummyBulletPoint("Integrated third-party APIs to enhance application functionality and user experience"),
        DummyBulletPoint("Collaborated with UX/UI designers to implement intuitive and accessible user interfaces")
    ])

    sample_resume.experiences.extend(experiences)

    # Add education with complete details
    educations = [
        DummyEducation(
            "University of Technology",
            "Boston, MA",
            "Master of Science",
            "Computer Science",
            "master",
            date(2016, 5, 15),
            3.92,
            date(2014, 9, 1)
        ),
        DummyEducation(
            "State University",
            "Los Angeles, CA",
            "Bachelor of Science",
            "Software Engineering",
            "bachelor",
            date(2014, 6, 15),
            3.8,
            date(2010, 9, 1)
        )
    ]
    sample_resume.educations.extend(educations)

    # Add skills with all skill types
    skills = [
        # Technical skills
        DummySkill("JavaScript", "technical", 95),
        DummySkill("Python", "language", 90),
        DummySkill("React", "language", 85),
        DummySkill("Node.js", "language", 85),
        DummySkill("TypeScript", "language", 80),
        DummySkill("Django", "technical", 80),
        DummySkill("RESTful APIs", "technical", 90),
        DummySkill("GraphQL", "technical", 75),
        DummySkill("PostgreSQL", "technical", 85),
        DummySkill("MongoDB", "technical", 80),

        # Tools
        DummySkill("AWS", "tool", 85),
        DummySkill("Docker", "tool", 80),
        DummySkill("Kubernetes", "tool", 75),
        DummySkill("Git", "tool", 90),
        DummySkill("Jenkins", "tool", 80),
        DummySkill("JIRA", "tool", 85),

        # Soft skills
        DummySkill("Team Leadership", "soft", 90),
        DummySkill("Project Management", "soft", 85),
        DummySkill("Communication", "soft", 95),
        DummySkill("Problem Solving", "soft", 90),
        DummySkill("Agile Methodologies", "soft", 85)
    ]
    sample_resume.skills.extend(skills)

    # Add projects with technologies
    projects = [
        DummyProject(
            "E-commerce Analytics Dashboard",
            "A responsive web application that visualizes sales data and customer insights for online retailers",
            date(2022, 3, 1),
            date(2022, 8, 15),
            "https://dashboard-demo.example.com",
            "https://github.com/example/analytics-dashboard"
        ),
        DummyProject(
            "Content Management System",
            "A customizable CMS with advanced user permissions and real-time collaboration features",
            date(2021, 5, 1),
            date(2021, 12, 10),
            "https://cms-example.com",
            "https://github.com/example/modern-cms"
        )
    ]

    # Add bullet points to projects
    projects[0].bullet_points.extend([
        DummyBulletPoint(
            "Designed and implemented interactive data visualizations using D3.js and React, providing actionable insights on sales trends"),
        DummyBulletPoint(
            "Integrated with RESTful APIs to fetch real-time sales and inventory data from multiple sources"),
        DummyBulletPoint("Implemented user authentication and role-based access control to ensure data security"),
        DummyBulletPoint("Created a responsive design that works seamlessly across desktop and mobile devices")
    ])

    projects[1].bullet_points.extend([
        DummyBulletPoint("Developed a plugin-based architecture allowing for easy extension of core functionality"),
        DummyBulletPoint("Implemented real-time collaboration features using WebSockets and Redis"),
        DummyBulletPoint("Created a customizable workflow engine to support complex content approval processes"),
        DummyBulletPoint("Optimized performance using lazy loading and efficient caching strategies")
    ])

    # Add technologies to projects
    tech_map = {
        "React": "technical",
        "Node.js": "technical",
        "MongoDB": "technical",
        "Express.js": "technical",
        "D3.js": "technical",
        "Redis": "technical",
        "AWS S3": "tool",
        "Docker": "tool"
    }

    for tech_name, tech_type in list(tech_map.items())[:4]:  # First 4 for project 1
        projects[0].technologies.append(DummySkill(tech_name, tech_type, 85))

    for tech_name, tech_type in list(tech_map.items())[4:]:  # Last 4 for project 2
        projects[1].technologies.append(DummySkill(tech_name, tech_type, 85))

    sample_resume.projects.extend(projects)

    # Add certifications with all fields
    certifications = [
        DummyCertification(
            "AWS Certified Solutions Architect - Professional",
            "Amazon Web Services",
            date(2022, 4, 10),
            date(2025, 4, 10),
            "Professional certification validating expertise in designing distributed systems on AWS",
            "https://aws.amazon.com/certification/certified-solutions-architect-professional/",
            "950/1000"
        ),
        DummyCertification(
            "Certified Kubernetes Administrator",
            "Cloud Native Computing Foundation",
            date(2021, 8, 15),
            date(2024, 8, 15),
            "Certification for Kubernetes administration and deployment expertise",
            "https://www.cncf.io/certification/cka/",
            "92%"
        )
    ]
    sample_resume.certifications.extend(certifications)

    # Add languages
    languages = [
        DummyLanguage("English", "native"),
        DummyLanguage("Spanish", "advanced"),
        DummyLanguage("French", "intermediate"),
        DummyLanguage("Mandarin", "basic")
    ]
    sample_resume.languages.extend(languages)

    # Add custom data sections
    custom_data_sections = [
        DummyCustomData(
            "Volunteer Experience",
            date(2022, 8, 1),
            "Developed a donation tracking system for a local food bank\nCreated a volunteer management application for disaster relief coordination\nMentored high school students in programming basics through weekly workshops",
            "Volunteered with Code for Good to develop web applications for non-profit organizations",
            "https://codeforgood.example.org",
            "Code for Good"
        ),
        DummyCustomData(
            "Publications",
            date(2021, 3, 15),
            "Published 'Scalable Architecture Patterns for Modern Web Applications' in Journal of Software Engineering\nContributed to 'Best Practices in Microservices Design' technical white paper\nAuthored multiple technical blog posts on Medium's Better Programming publication",
            "Technical publications related to software architecture and development",
            "https://medium.com/@alexmorgan",
            "Various Publishers"
        ),
        DummyCustomData(
            "Awards & Recognition",
            date(2021, 11, 10),
            "Developer of the Year, Company Awards 2021\nHackathon Winner, Healthcare Innovation Challenge 2020\nRecognized for Outstanding Technical Leadership, Q3 2019",
            "Professional recognition and awards received throughout career"
        )
    ]
    sample_resume.custom_data.extend(custom_data_sections)

    # Modify DummyQuerySet to support template regroup tag
    sample_resume.skills.get_skill_type_display = lambda: 'Technical'

    return sample_resume


def create_fresher_resume():
    """Create a sample resume for a fresh graduate with appropriate data."""
    from datetime import date

    class DummyQuerySet(list):
        def exists(self):
            return len(self) > 0

        def all(self):
            return self

        def get_skill_type_display(self):
            return self.skill_type.capitalize() if hasattr(self, 'skill_type') else ""

    class DummyBulletPoint:
        def __init__(self, description):
            self.description = description
            self.keywords = DummyQuerySet()

    class DummyExperience:
        def __init__(self, job_title, employer, location, start_date, end_date=None, is_current=False):
            self.job_title = job_title
            self.employer = employer
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.is_current = is_current
            self.bullet_points = DummyQuerySet()

    class DummyEducation:
        def __init__(self, school_name, location, degree, field_of_study, degree_type, graduation_date, gpa=None,
                     start_date=None):
            self.school_name = school_name
            self.location = location
            self.degree = degree
            self.field_of_study = field_of_study
            self.degree_type = degree_type
            self.graduation_date = graduation_date
            self.start_date = start_date
            self.gpa = gpa
            self.achievements = "Dean's List: 2022-2023\nCompleted final project with highest honors\nSelected for prestigious internship program\nWon 2nd place in university hackathon"

    class DummySkill:
        def __init__(self, name, skill_type, proficiency_level):
            self.skill_name = name
            self.skill_type = skill_type
            self.proficiency_level = proficiency_level

        def get_skill_type_display(self):
            types = {
                'technical': 'Technical',
                'soft': 'Soft',
                'language': 'Language',
                'tool': 'Tool'
            }
            return types.get(self.skill_type, self.skill_type)

    class DummyProject:
        def __init__(self, name, summary, start_date, completion_date, project_link=None, github_link=None):
            self.project_name = name
            self.summary = summary
            self.start_date = start_date
            self.completion_date = completion_date
            self.project_link = project_link
            self.github_link = github_link
            self.bullet_points = DummyQuerySet()
            self.technologies = DummyQuerySet()

    class DummyCertification:
        def __init__(self, name, institute, completion_date, expiration_date=None, description=None, link=None,
                     score=None):
            self.name = name
            self.institute = institute
            self.completion_date = completion_date
            self.expiration_date = expiration_date
            self.description = description
            self.link = link
            self.score = score

    class DummyLanguage:
        def __init__(self, name, proficiency):
            self.language_name = name
            self.proficiency = proficiency

        def get_proficiency_display(self):
            return {"basic": "Basic", "intermediate": "Intermediate",
                    "advanced": "Advanced", "native": "Native"}[self.proficiency]

    class DummyCustomData:
        def __init__(self, name, completion_date=None, bullet_points=None, description=None, link=None,
                     institution_name=None):
            self.name = name
            self.completion_date = completion_date
            self.bullet_points = bullet_points
            self.description = description
            self.link = link
            self.institution_name = institution_name

    class DummyResume:
        def __init__(self):
            self.id = 1
            self.first_name = "Jamie"
            self.mid_name = ""
            self.last_name = "Taylor"
            self.full_name = "Jamie Taylor"
            self.title = "Computer Science Graduate"
            self.email = "jamie.taylor@example.com"
            self.phone = "(555) 987-6543"
            self.address = "123 University Ave, Boston, MA 02215"
            self.linkedin = "https://linkedin.com/in/jamietaylor"
            self.github = "https://github.com/jamietaylor"
            self.portfolio = "https://jamietaylor.dev"
            self.summary = "Recent Computer Science graduate with strong foundations in programming, algorithms, and web development. Completed multiple projects showcasing skills in Python, Java, and JavaScript. Eager to apply academic knowledge and technical abilities in a professional software development role to build innovative and efficient solutions."

            # Initialize collections
            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.skills = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_data = DummyQuerySet()

    # Create fresh graduate resume
    fresher_resume = DummyResume()

    # Add education (primary focus for a fresher resume)
    education = DummyEducation(
        "Boston University",
        "Boston, MA",
        "Bachelor of Science",
        "Computer Science",
        "bachelor",
        date(2023, 5, 15),  # Recent graduation
        3.8,
        date(2019, 9, 1)
    )
    fresher_resume.educations.append(education)

    # Add internship experience (limited experience for a fresher)
    internship = DummyExperience(
        "Software Development Intern",
        "TechStart Solutions",
        "Boston, MA",
        date(2022, 6, 1),
        date(2022, 8, 31),
        False
    )
    internship.bullet_points.extend([
        DummyBulletPoint(
            "Assisted in developing and testing features for the company's e-commerce platform using React and Node.js"),
        DummyBulletPoint(
            "Participated in daily scrum meetings and collaborated with senior developers on code reviews"),
        DummyBulletPoint("Implemented responsive design improvements that enhanced mobile user experience by 25%")
    ])
    fresher_resume.experiences.append(internship)

    # Add part-time job during studies
    part_time = DummyExperience(
        "Computer Lab Assistant",
        "Boston University IT Department",
        "Boston, MA",
        date(2021, 9, 1),
        date(2023, 5, 15),
        False
    )
    part_time.bullet_points.extend([
        DummyBulletPoint("Provided technical support to students and faculty for hardware and software issues"),
        DummyBulletPoint("Maintained computer lab equipment and assisted in software installations and updates"),
        DummyBulletPoint("Conducted basic programming tutoring sessions for introductory CS courses")
    ])
    fresher_resume.experiences.append(part_time)

    # Add projects (important for freshers to showcase skills)
    project1 = DummyProject(
        "Student Management System",
        "A full-stack web application for managing student records, courses, and grades",
        date(2022, 9, 1),
        date(2023, 4, 30),
        "https://student-ms-demo.example.com",
        "https://github.com/jamietaylor/student-ms"
    )
    project1.bullet_points.extend([
        DummyBulletPoint(
            "Designed and implemented a database schema with MySQL to store student and course information"),
        DummyBulletPoint(
            "Developed a responsive front-end using React and Bootstrap that allows for intuitive navigation"),
        DummyBulletPoint(
            "Implemented secure user authentication with different permission levels for students and administrators")
    ])
    project1.technologies.extend([
        DummySkill("React", "technical", 80),
        DummySkill("Node.js", "technical", 75),
        DummySkill("MySQL", "technical", 85),
        DummySkill("Bootstrap", "technical", 90)
    ])

    project2 = DummyProject(
        "Weather Forecast Mobile App",
        "A cross-platform mobile application showing detailed weather forecasts and alerts",
        date(2021, 11, 1),
        date(2022, 2, 28),
        "https://weather-app-demo.example.com",
        "https://github.com/jamietaylor/weather-app"
    )
    project2.bullet_points.extend([
        DummyBulletPoint("Created a cross-platform mobile app using Flutter that fetches and displays weather data"),
        DummyBulletPoint("Integrated with OpenWeatherMap API to retrieve real-time weather information"),
        DummyBulletPoint("Implemented location-based services to automatically detect the user's current location")
    ])
    project2.technologies.extend([
        DummySkill("Flutter", "technical", 75),
        DummySkill("Dart", "language", 70),
        DummySkill("REST APIs", "technical", 80),
        DummySkill("Firebase", "tool", 65)
    ])



    fresher_resume.projects.extend([project1, project2])

    # Add skills (focus on skills relevant for entry-level positions)
    skills = [
        # Programming languages
        DummySkill("Java", "language", 85),
        DummySkill("Python", "language", 90),
        DummySkill("JavaScript", "language", 80),
        DummySkill("HTML/CSS", "language", 85),
        DummySkill("SQL", "language", 75),
        DummySkill("C++", "language", 70),

        # Technical skills
        DummySkill("Data Structures", "technical", 85),
        DummySkill("Algorithms", "technical", 80),
        DummySkill("Object-Oriented Programming", "technical", 85),
        DummySkill("Web Development", "technical", 80),
        DummySkill("Mobile Development", "technical", 75),
        DummySkill("Database Design", "technical", 70),

        # Tools and frameworks
        DummySkill("Git", "tool", 85),
        DummySkill("React", "tool", 75),
        DummySkill("Node.js", "tool", 70),
        DummySkill("Flutter", "tool", 65),
        DummySkill("Docker", "tool", 60),
        DummySkill("VS Code", "tool", 90),

        # Soft skills
        DummySkill("Problem Solving", "soft", 85),
        DummySkill("Teamwork", "soft", 90),
        DummySkill("Communication", "soft", 85),
        DummySkill("Time Management", "soft", 80),
        DummySkill("Adaptability", "soft", 85)
    ]
    fresher_resume.skills.extend(skills)

    # Add certifications (entry-level certifications)
    certifications = [
        DummyCertification(
            "AWS Certified Cloud Practitioner",
            "Amazon Web Services",
            date(2023, 1, 15),
            date(2026, 1, 15),
            "Foundational certification validating understanding of AWS Cloud",
            "https://aws.amazon.com/certification/certified-cloud-practitioner/",
            "820/1000"
        ),
        DummyCertification(
            "Oracle Certified Associate Java Programmer",
            "Oracle",
            date(2022, 6, 10),
            None,
            "Entry-level certification for Java programming language",
            "https://education.oracle.com/java-certification-path",
            "85%"
        ),
        DummyCertification(
            "Microsoft Certified: Azure Fundamentals",
            "Microsoft",
            date(2022, 11, 20),
            None,
            "Basic understanding of cloud services and Microsoft Azure",
            "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/",
            "875/1000"
        )
    ]
    fresher_resume.certifications.extend(certifications)

    # Add languages
    languages = [
        DummyLanguage("English", "native"),
        DummyLanguage("Spanish", "intermediate"),
        DummyLanguage("French", "basic")
    ]
    fresher_resume.languages.extend(languages)

    # Add extracurricular activities and achievements (important for freshers)
    custom_data_sections = [
        DummyCustomData(
            "Extracurricular Activities",
            date(2023, 5, 1),
            "Member of the University Coding Club (2021-2023)\nParticipated in three Hackathons, winning 2nd place in CodeJam 2022\nVolunteered as a peer mentor for first-year Computer Science students\nContributed to open-source projects on GitHub",
            "Active participation in university and community technical activities",
            None,
            "Boston University"
        ),

    ]
    fresher_resume.custom_data.extend(custom_data_sections)

    # Modify DummyQuerySet to support template regroup tag
    fresher_resume.skills.get_skill_type_display = lambda: 'Technical'

    return fresher_resume

def get_language_template(request):
    """
    Returns the HTML template for a new language form row
    """
    # Get the index from the request (defaulting to 0 if not provided)
    index = request.GET.get('index', 0)

    # Define proficiency levels for the dropdown
    proficiency_levels = {
        'native': 'Native/Fluent',
        'advanced': 'Advanced/Professional',
        'intermediate': 'Intermediate',
        'basic': 'Basic/Elementary'
    }

    # Render the language form template
    return render(request, 'resumes/partials/form_rows/language_form_row.html', {
        'index': index,
        'proficiency_levels': proficiency_levels,
        'forloop': {'counter0': index, 'counter': int(index) + 1}  # Simulate forloop context for the template
    })
