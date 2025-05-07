


# resumes/views.py

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET", "POST"])
@login_required
@require_http_methods(["GET", "POST"])
def preview_current_resume(request):
    """
    Generate a live preview of the resume with all available data from session and current form.
    This view merges data from previous steps stored in the session with the current form data.
    """
    # Get template ID from session
    template_id = request.session.get('resume_template_id')
    if not template_id:
        return HttpResponse("<div class='p-4 text-center text-red-500'>Please select a template first.</div>")

    # Get ALL stored form data from session - this is crucial to get data from previous steps
    form_data = request.session.get('resume_form_data', {})

    # If this is a POST request, merge current form data without overwriting saved data
    if request.method == 'POST':
        # Save current form data to the relevant section in form_data
        current_step = request.session.get('resume_wizard_step', 1)

        if current_step == 1:  # Personal info
            personal_info = {}
            for key in ['first_name', 'mid_name', 'last_name', 'email', 'phone', 'address',
                        'linkedin', 'github', 'portfolio']:
                if key in request.POST:
                    personal_info[key] = request.POST.get(key)

            if personal_info:
                form_data['personal_info'] = personal_info

        elif current_step == 2:  # Summary
            if 'summary' in request.POST:
                form_data['summary'] = request.POST.get('summary')

        elif current_step == 3:  # Skills
            # Process skills data from the form
            skills_data = []
            skill_count = int(request.POST.get('skill_count', 0))

            for i in range(skill_count):
                if request.POST.get(f'skill_name_{i}'):
                    skill = {
                        'skill_name': request.POST.get(f'skill_name_{i}'),
                        'skill_type': request.POST.get(f'skill_type_{i}'),
                        'proficiency_level': request.POST.get(f'proficiency_level_{i}'),
                    }
                    skills_data.append(skill)

            # Save skills data to session
            if skills_data:
                form_data['skills'] = skills_data

        elif current_step == 4:  # Work Experience
            # Process experience data from the form
            experience_data = []
            experience_count = int(request.POST.get('experience_count', 0))

            for i in range(experience_count):
                if request.POST.get(f'job_title_{i}'):
                    # Get bullet points for this experience
                    bullet_points = []
                    bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))

                    for j in range(bullet_count):
                        bullet_text = request.POST.get(f'bullet_{i}_{j}')
                        if bullet_text:
                            bullet_points.append(bullet_text)

                    # Create experience entry with bullet points
                    experience = {
                        'job_title': request.POST.get(f'job_title_{i}'),
                        'employer': request.POST.get(f'employer_{i}'),
                        'location': request.POST.get(f'location_{i}'),
                        'start_date': request.POST.get(f'start_date_{i}'),
                        'end_date': request.POST.get(f'end_date_{i}'),
                        'is_current': request.POST.get(f'is_current_{i}') == 'on',
                        'bullet_points': bullet_points
                    }
                    experience_data.append(experience)

            # Save experience data to session
            if experience_data:
                form_data['experiences'] = experience_data

        elif current_step == 5:  # Education
            # Process education data from the form
            education_data = []
            education_count = int(request.POST.get('education_count', 0))

            for i in range(education_count):
                if request.POST.get(f'school_name_{i}'):
                    education = {
                        'school_name': request.POST.get(f'school_name_{i}'),
                        'location': request.POST.get(f'location_{i}'),
                        'degree': request.POST.get(f'degree_{i}'),
                        'degree_type': request.POST.get(f'degree_type_{i}'),
                        'field_of_study': request.POST.get(f'field_of_study_{i}'),
                        'graduation_date': request.POST.get(f'graduation_date_{i}'),
                        'gpa': request.POST.get(f'gpa_{i}'),
                    }
                    education_data.append(education)

            # Save education data to session
            if education_data:
                form_data['educations'] = education_data

        elif current_step == 6:  # Projects
            # Process project data from the form
            project_data = []
            project_count = int(request.POST.get('project_count', 0))

            for i in range(project_count):
                if request.POST.get(f'project_name_{i}'):
                    # Get bullet points for this project
                    bullet_points = []
                    bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))

                    for j in range(bullet_count):
                        bullet_text = request.POST.get(f'bullet_{i}_{j}')
                        if bullet_text:
                            bullet_points.append(bullet_text)

                    # Create project entry with bullet points
                    project = {
                        'project_name': request.POST.get(f'project_name_{i}'),
                        'summary': request.POST.get(f'summary_{i}'),
                        'start_date': request.POST.get(f'start_date_{i}'),
                        'completion_date': request.POST.get(f'completion_date_{i}'),
                        'project_link': request.POST.get(f'project_link_{i}'),
                        'github_link': request.POST.get(f'github_link_{i}'),
                        'bullet_points': bullet_points,
                    }
                    project_data.append(project)

            # Save project data to session
            if project_data:
                form_data['projects'] = project_data

        elif current_step == 7:  # Certifications
            # Process certification data from the form
            certification_data = []
            certification_count = int(request.POST.get('certification_count', 0))

            for i in range(certification_count):
                if request.POST.get(f'name_{i}'):
                    certification = {
                        'name': request.POST.get(f'name_{i}'),
                        'institute': request.POST.get(f'institute_{i}'),
                        'completion_date': request.POST.get(f'completion_date_{i}'),
                        'expiration_date': request.POST.get(f'expiration_date_{i}'),
                        'score': request.POST.get(f'score_{i}'),
                        'link': request.POST.get(f'link_{i}'),
                        'description': request.POST.get(f'description_{i}'),
                    }
                    certification_data.append(certification)

            # Save certification data to session
            if certification_data:
                form_data['certifications'] = certification_data

        elif current_step == 8:  # Languages
            # Process language data from the form
            language_data = []
            language_count = int(request.POST.get('language_count', 0))

            for i in range(language_count):
                if request.POST.get(f'language_name_{i}'):
                    language = {
                        'language_name': request.POST.get(f'language_name_{i}'),
                        'proficiency': request.POST.get(f'proficiency_{i}'),
                    }
                    language_data.append(language)

            # Save language data to session
            if language_data:
                form_data['languages'] = language_data

        elif current_step == 9:  # Custom Sections
            # Process custom section data from the form
            custom_data = []
            section_count = int(request.POST.get('section_count', 0))

            for i in range(section_count):
                if request.POST.get(f'name_{i}'):
                    section = {
                        'name': request.POST.get(f'name_{i}'),
                        'completion_date': request.POST.get(f'completion_date_{i}'),
                        'bullet_points': request.POST.get(f'bullet_points_{i}'),
                        'description': request.POST.get(f'description_{i}'),
                        'link': request.POST.get(f'link_{i}'),
                        'institution_name': request.POST.get(f'institution_name_{i}'),
                    }
                    custom_data.append(section)

            # Save custom section data to session
            if custom_data:
                form_data['custom_sections'] = custom_data

    # Helper function to clean data strings
    def clean_data_string(value):
        """Clean strings that might contain JSON-like formatting or escape sequences"""
        if not isinstance(value, str):
            return value

        # Check if it looks like a JSON string and try to parse it
        if value.startswith('{') and value.endswith('}'):
            try:
                import json
                # Replace single quotes with double quotes for proper JSON parsing
                json_str = value.replace("'", '"')
                data_dict = json.loads(json_str)

                # If we have a dictionary with a specific key, extract it
                for key in ['summary', 'description', 'bullet_points']:
                    if key in data_dict:
                        value = data_dict[key]
                        break
            except:
                # If JSON parsing fails, keep the original string
                pass

        # Clean escape sequences
        if isinstance(value, str):
            value = (value.replace('\\r\\n', '\n')
                     .replace('\\n', '\n')
                     .replace('\\r', '\n')
                     .replace('\\"', '"')
                     .replace("\\'", "'"))

        return value

    # Create dummy classes for mimicking the model structure
    class DummyQuerySet(list):
        def exists(self):
            return len(self) > 0

        def all(self):
            return self

    class DummyBulletPoint:
        def __init__(self, description):
            self.description = clean_data_string(description)

    class DummySkill:
        def __init__(self, data):
            self.skill_name = clean_data_string(data.get('skill_name', ''))
            self.skill_type = clean_data_string(data.get('skill_type', 'technical'))
            self.proficiency_level = data.get('proficiency_level', 0)

        def get_skill_type_display(self):
            types = {
                'technical': 'Technical',
                'soft': 'Soft',
                'language': 'Language',
                'tool': 'Tool'
            }
            return types.get(self.skill_type, self.skill_type)

    class DummyExperience:
        def __init__(self, data):
            from datetime import datetime

            self.job_title = clean_data_string(data.get('job_title', ''))
            self.employer = clean_data_string(data.get('employer', ''))
            self.location = clean_data_string(data.get('location', ''))

            # Process start date
            start_date_str = data.get('start_date', '')
            if start_date_str:
                try:
                    date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    self.start_date = date_obj
                except (ValueError, TypeError):
                    self.start_date = start_date_str
            else:
                self.start_date = None

            # Handle is_current flag
            self.is_current = data.get('is_current', False)
            if isinstance(self.is_current, str):
                self.is_current = self.is_current.lower() in ['on', 'true', '1', 'yes']

            # Process end date
            end_date_str = data.get('end_date', '')
            if end_date_str and not self.is_current:
                try:
                    date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    self.end_date = date_obj
                except (ValueError, TypeError):
                    self.end_date = end_date_str
            else:
                self.end_date = None

            # Create formatted dates for display
            self.formatted_start_date = self._format_date(self.start_date)
            self.formatted_end_date = 'Present' if self.is_current else self._format_date(self.end_date)

            # Create a formatted date range string
            if self.formatted_start_date:
                if self.is_current:
                    self.date_range = f"{self.formatted_start_date} - Present"
                elif self.formatted_end_date:
                    self.date_range = f"{self.formatted_start_date} - {self.formatted_end_date}"
                else:
                    self.date_range = self.formatted_start_date
            else:
                self.date_range = ""

            # Add bullet points
            self.bullet_points = DummyQuerySet()
            for bp_text in data.get('bullet_points', []):
                self.bullet_points.append(DummyBulletPoint(bp_text))

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyEducation:
        def __init__(self, data):
            from datetime import datetime

            self.school_name = clean_data_string(data.get('school_name', ''))
            self.location = clean_data_string(data.get('location', ''))
            self.degree = clean_data_string(data.get('degree', ''))
            self.degree_type = clean_data_string(data.get('degree_type', 'bachelor'))
            self.field_of_study = clean_data_string(data.get('field_of_study', ''))

            # Process graduation date
            grad_date_str = data.get('graduation_date', '')
            if grad_date_str:
                try:
                    date_obj = datetime.strptime(grad_date_str, '%Y-%m-%d').date()
                    self.graduation_date = date_obj
                except (ValueError, TypeError):
                    self.graduation_date = grad_date_str
            else:
                self.graduation_date = None

            self.formatted_graduation_date = self._format_date(self.graduation_date)
            self.gpa = data.get('gpa', '')

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyProject:
        def __init__(self, data):
            from datetime import datetime

            self.project_name = clean_data_string(data.get('project_name', ''))
            self.summary = clean_data_string(data.get('summary', ''))

            # Process start date
            start_date_str = data.get('start_date', '')
            if start_date_str:
                try:
                    date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    self.start_date = date_obj
                except (ValueError, TypeError):
                    self.start_date = start_date_str
            else:
                self.start_date = None

            # Process completion date
            completion_date_str = data.get('completion_date', '')
            if completion_date_str:
                try:
                    date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                    self.completion_date = date_obj
                except (ValueError, TypeError):
                    self.completion_date = completion_date_str
            else:
                self.completion_date = None

            # Create formatted dates
            self.formatted_start_date = self._format_date(self.start_date)
            self.formatted_completion_date = self._format_date(self.completion_date)

            # Create a date range string
            if self.formatted_start_date and self.formatted_completion_date:
                self.date_range = f"{self.formatted_start_date} - {self.formatted_completion_date}"
            elif self.formatted_start_date:
                self.date_range = f"{self.formatted_start_date} - Present"
            else:
                self.date_range = ""

            self.project_link = clean_data_string(data.get('project_link', ''))
            self.github_link = clean_data_string(data.get('github_link', ''))
            self.bullet_points = DummyQuerySet()

            # Add bullet points
            for bp_text in data.get('bullet_points', []):
                self.bullet_points.append(DummyBulletPoint(bp_text))

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyCertification:
        def __init__(self, data):
            from datetime import datetime

            self.name = clean_data_string(data.get('name', ''))
            self.institute = clean_data_string(data.get('institute', ''))

            # Process completion date
            completion_date_str = data.get('completion_date', '')
            if completion_date_str:
                try:
                    date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                    self.completion_date = date_obj
                except (ValueError, TypeError):
                    self.completion_date = completion_date_str
            else:
                self.completion_date = None

            # Process expiration date
            expiration_date_str = data.get('expiration_date', '')
            if expiration_date_str:
                try:
                    date_obj = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                    self.expiration_date = date_obj
                except (ValueError, TypeError):
                    self.expiration_date = expiration_date_str
            else:
                self.expiration_date = None

            # Create formatted dates
            self.formatted_completion_date = self._format_date(self.completion_date)
            self.formatted_expiration_date = self._format_date(self.expiration_date)

            self.score = clean_data_string(data.get('score', ''))
            self.link = clean_data_string(data.get('link', ''))
            self.description = clean_data_string(data.get('description', ''))

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyLanguage:
        def __init__(self, data):
            self.language_name = clean_data_string(data.get('language_name', ''))
            self.proficiency = clean_data_string(data.get('proficiency', 'basic'))

        def get_proficiency_display(self):
            levels = {
                'basic': 'Basic',
                'intermediate': 'Intermediate',
                'advanced': 'Advanced',
                'native': 'Native'
            }
            return levels.get(self.proficiency, self.proficiency)

    class DummyCustomData:
        def __init__(self, data):
            from datetime import datetime

            self.name = clean_data_string(data.get('name', ''))

            # Process completion date
            completion_date_str = data.get('completion_date', '')
            if completion_date_str:
                try:
                    date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                    self.completion_date = date_obj
                except (ValueError, TypeError):
                    self.completion_date = completion_date_str
            else:
                self.completion_date = None

            # Create formatted date
            self.formatted_completion_date = self._format_date(self.completion_date)

            # Clean and properly format the bullet points
            self.bullet_points = clean_data_string(data.get('bullet_points', ''))
            self.description = clean_data_string(data.get('description', ''))
            self.link = clean_data_string(data.get('link', ''))
            self.institution_name = clean_data_string(data.get('institution_name', ''))

        def _format_date(self, date_obj):
            """Format date object to 'Mon YYYY' format"""
            if not date_obj:
                return ""

            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%b %Y')
            return str(date_obj)

    class DummyResume:
        def __init__(self):
            # Add personal info attributes
            personal_info = form_data.get('personal_info', {})
            self.first_name = clean_data_string(personal_info.get('first_name', ''))
            self.mid_name = clean_data_string(personal_info.get('mid_name', ''))
            self.last_name = clean_data_string(personal_info.get('last_name', ''))
            self.full_name = f"{self.first_name} {self.mid_name} {self.last_name}".strip()
            self.email = clean_data_string(personal_info.get('email', ''))
            self.phone = clean_data_string(personal_info.get('phone', ''))
            self.address = clean_data_string(personal_info.get('address', ''))
            self.linkedin = clean_data_string(personal_info.get('linkedin', ''))
            self.github = clean_data_string(personal_info.get('github', ''))
            self.portfolio = clean_data_string(personal_info.get('portfolio', ''))

            # Add summary
            self.summary = clean_data_string(form_data.get('summary', ''))

            # Initialize collections
            self.skills = DummyQuerySet()
            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_data = DummyQuerySet()

            # Populate skills
            for skill_data in form_data.get('skills', []):
                self.skills.append(DummySkill(skill_data))

            # Populate experiences
            for exp_data in form_data.get('experiences', []):
                self.experiences.append(DummyExperience(exp_data))

            # Populate educations
            for edu_data in form_data.get('educations', []):
                self.educations.append(DummyEducation(edu_data))

            # Populate projects
            for proj_data in form_data.get('projects', []):
                self.projects.append(DummyProject(proj_data))

            # Populate certifications
            for cert_data in form_data.get('certifications', []):
                self.certifications.append(DummyCertification(cert_data))

            # Populate languages
            for lang_data in form_data.get('languages', []):
                self.languages.append(DummyLanguage(lang_data))

            # Populate custom data
            for custom_data in form_data.get('custom_sections', []):
                self.custom_data.append(DummyCustomData(custom_data))

    resume = DummyResume()

    try:
        # Use a more reliable template path that matches your project structure
        return render(request, f'resumes/templates/template{template_id}.html', {
            'resume': resume,
            'is_preview': True
        })
    except Exception as e:
        # Return error message
        error_html = f"""
        <div class="p-4 text-center">
            <h4 class="text-red-500 font-bold mb-2">Error Rendering Template</h4>
            <p class="text-gray-600 mb-2">There was a problem generating your resume preview:</p>
            <div class="bg-gray-100 p-3 rounded text-left text-sm text-gray-700 mb-4">
                <code>{str(e)}</code>
            </div>
            <p class="text-sm text-gray-500">Template path attempted: resumes/templates/template{template_id}.html</p>
        </div>
        """
        return HttpResponse(error_html)
# def preview_current_resume(request):
#     """
#     Generate a live preview of the resume with all available data from session and current form.
#     This view merges data from previous steps stored in the session with the current form data.
#     """
#     # Get template ID from session
#     template_id = request.session.get('resume_template_id')
#     if not template_id:
#         return HttpResponse("<div class='p-4 text-center text-red-500'>Please select a template first.</div>")
#
#     # Get ALL stored form data from session - this is crucial to get data from previous steps
#     form_data = request.session.get('resume_form_data', {})
#
#     # If this is a POST request, merge current form data without overwriting saved data
#     if request.method == 'POST':
#         # Save current form data to the relevant section in form_data
#         current_step = request.session.get('resume_wizard_step', 1)
#
#         if current_step == 1:  # Personal info
#             personal_info = {}
#             for key in ['first_name', 'mid_name', 'last_name', 'email', 'phone', 'address',
#                         'linkedin', 'github', 'portfolio']:
#                 if key in request.POST:
#                     personal_info[key] = request.POST.get(key)
#
#             if personal_info:
#                 form_data['personal_info'] = personal_info
#
#         elif current_step == 2:  # Summary
#             if 'summary' in request.POST:
#                 form_data['summary'] = request.POST.get('summary')
#
#         elif current_step == 3:  # Skills
#             # Process skills data from the form
#             skills_data = []
#             skill_count = int(request.POST.get('skill_count', 0))
#
#             for i in range(skill_count):
#                 if request.POST.get(f'skill_name_{i}'):
#                     skill = {
#                         'skill_name': request.POST.get(f'skill_name_{i}'),
#                         'skill_type': request.POST.get(f'skill_type_{i}'),
#                         'proficiency_level': request.POST.get(f'proficiency_level_{i}'),
#                     }
#                     skills_data.append(skill)
#
#             # Save skills data to session
#             if skills_data:
#                 form_data['skills'] = skills_data
#
#         elif current_step == 4:  # Work Experience
#             # Process experience data from the form
#             experience_data = []
#             experience_count = int(request.POST.get('experience_count', 0))
#
#             for i in range(experience_count):
#                 if request.POST.get(f'job_title_{i}'):
#                     # Get bullet points for this experience
#                     bullet_points = []
#                     bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))
#
#                     for j in range(bullet_count):
#                         bullet_text = request.POST.get(f'bullet_{i}_{j}')
#                         if bullet_text:
#                             bullet_points.append(bullet_text)
#
#                     # Create experience entry with bullet points
#                     experience = {
#                         'job_title': request.POST.get(f'job_title_{i}'),
#                         'employer': request.POST.get(f'employer_{i}'),
#                         'location': request.POST.get(f'location_{i}'),
#                         'start_date': request.POST.get(f'start_date_{i}'),
#                         'end_date': request.POST.get(f'end_date_{i}'),
#                         'is_current': request.POST.get(f'is_current_{i}') == 'on',
#                         'bullet_points': bullet_points
#                     }
#                     experience_data.append(experience)
#
#             # Save experience data to session
#             if experience_data:
#                 form_data['experiences'] = experience_data
#
#         elif current_step == 5:  # Education
#             # Process education data from the form
#             education_data = []
#             education_count = int(request.POST.get('education_count', 0))
#
#             for i in range(education_count):
#                 if request.POST.get(f'school_name_{i}'):
#                     education = {
#                         'school_name': request.POST.get(f'school_name_{i}'),
#                         'location': request.POST.get(f'location_{i}'),
#                         'degree': request.POST.get(f'degree_{i}'),
#                         'degree_type': request.POST.get(f'degree_type_{i}'),
#                         'field_of_study': request.POST.get(f'field_of_study_{i}'),
#                         'graduation_date': request.POST.get(f'graduation_date_{i}'),
#                         'gpa': request.POST.get(f'gpa_{i}'),
#                     }
#                     education_data.append(education)
#
#             # Save education data to session
#             if education_data:
#                 form_data['educations'] = education_data
#
#         elif current_step == 6:  # Projects
#             # Process project data from the form
#             project_data = []
#             project_count = int(request.POST.get('project_count', 0))
#
#             for i in range(project_count):
#                 if request.POST.get(f'project_name_{i}'):
#                     # Get bullet points for this project
#                     bullet_points = []
#                     bullet_count = int(request.POST.get(f'bullet_count_{i}', 0))
#
#                     for j in range(bullet_count):
#                         bullet_text = request.POST.get(f'bullet_{i}_{j}')
#                         if bullet_text:
#                             bullet_points.append(bullet_text)
#
#                     # Create project entry with bullet points
#                     project = {
#                         'project_name': request.POST.get(f'project_name_{i}'),
#                         'summary': request.POST.get(f'summary_{i}'),
#                         'start_date': request.POST.get(f'start_date_{i}'),
#                         'completion_date': request.POST.get(f'completion_date_{i}'),
#                         'project_link': request.POST.get(f'project_link_{i}'),
#                         'github_link': request.POST.get(f'github_link_{i}'),
#                         'bullet_points': bullet_points,
#                     }
#                     project_data.append(project)
#
#             # Save project data to session
#             if project_data:
#                 form_data['projects'] = project_data
#
#         elif current_step == 7:  # Certifications
#             # Process certification data from the form
#             certification_data = []
#             certification_count = int(request.POST.get('certification_count', 0))
#
#             for i in range(certification_count):
#                 if request.POST.get(f'name_{i}'):
#                     certification = {
#                         'name': request.POST.get(f'name_{i}'),
#                         'institute': request.POST.get(f'institute_{i}'),
#                         'completion_date': request.POST.get(f'completion_date_{i}'),
#                         'expiration_date': request.POST.get(f'expiration_date_{i}'),
#                         'score': request.POST.get(f'score_{i}'),
#                         'link': request.POST.get(f'link_{i}'),
#                         'description': request.POST.get(f'description_{i}'),
#                     }
#                     certification_data.append(certification)
#
#             # Save certification data to session
#             if certification_data:
#                 form_data['certifications'] = certification_data
#
#         elif current_step == 8:  # Languages
#             # Process language data from the form
#             language_data = []
#             language_count = int(request.POST.get('language_count', 0))
#
#             for i in range(language_count):
#                 if request.POST.get(f'language_name_{i}'):
#                     language = {
#                         'language_name': request.POST.get(f'language_name_{i}'),
#                         'proficiency': request.POST.get(f'proficiency_{i}'),
#                     }
#                     language_data.append(language)
#
#             # Save language data to session
#             if language_data:
#                 form_data['languages'] = language_data
#
#         elif current_step == 9:  # Custom Sections
#             # Process custom section data from the form
#             custom_data = []
#             section_count = int(request.POST.get('section_count', 0))
#
#             for i in range(section_count):
#                 if request.POST.get(f'name_{i}'):
#                     section = {
#                         'name': request.POST.get(f'name_{i}'),
#                         'completion_date': request.POST.get(f'completion_date_{i}'),
#                         'bullet_points': request.POST.get(f'bullet_points_{i}'),
#                         'description': request.POST.get(f'description_{i}'),
#                         'link': request.POST.get(f'link_{i}'),
#                         'institution_name': request.POST.get(f'institution_name_{i}'),
#                     }
#                     custom_data.append(section)
#
#             # Save custom section data to session
#             if custom_data:
#                 form_data['custom_sections'] = custom_data
#
#     # Create a dummy resume object for the template that mimics your model structure
#     class DummyQuerySet(list):
#         def exists(self):
#             return len(self) > 0
#
#         def all(self):
#             return self
#
#     class DummyBulletPoint:
#         def __init__(self, description):
#             self.description = description
#
#     class DummySkill:
#         def __init__(self, data):
#             self.skill_name = data.get('skill_name', '')
#             self.skill_type = data.get('skill_type', 'technical')
#             self.proficiency_level = data.get('proficiency_level', 0)
#
#         def get_skill_type_display(self):
#             types = {
#                 'technical': 'Technical',
#                 'soft': 'Soft',
#                 'language': 'Language',
#                 'tool': 'Tool'
#             }
#             return types.get(self.skill_type, self.skill_type)
#
#     class DummyExperience:
#         def __init__(self, data):
#             from datetime import datetime
#
#             self.job_title = data.get('job_title', '')
#             self.employer = data.get('employer', '')
#             self.location = data.get('location', '')
#
#             # Process start date
#             start_date_str = data.get('start_date', '')
#             if start_date_str:
#                 try:
#                     date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#                     self.start_date = date_obj
#                 except (ValueError, TypeError):
#                     self.start_date = start_date_str
#             else:
#                 self.start_date = None
#
#             # Handle is_current flag
#             self.is_current = data.get('is_current', False)
#             if isinstance(self.is_current, str):
#                 self.is_current = self.is_current.lower() in ['on', 'true', '1', 'yes']
#
#             # Process end date
#             end_date_str = data.get('end_date', '')
#             if end_date_str and not self.is_current:
#                 try:
#                     date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#                     self.end_date = date_obj
#                 except (ValueError, TypeError):
#                     self.end_date = end_date_str
#             else:
#                 self.end_date = None
#
#             # Create formatted dates for display
#             self.formatted_start_date = self._format_date(self.start_date)
#             self.formatted_end_date = 'Present' if self.is_current else self._format_date(self.end_date)
#
#             # Create a formatted date range string
#             if self.formatted_start_date:
#                 if self.is_current:
#                     self.date_range = f"{self.formatted_start_date} - Present"
#                 elif self.formatted_end_date:
#                     self.date_range = f"{self.formatted_start_date} - {self.formatted_end_date}"
#                 else:
#                     self.date_range = self.formatted_start_date
#             else:
#                 self.date_range = ""
#
#             # Add bullet points
#             self.bullet_points = DummyQuerySet()
#             for bp_text in data.get('bullet_points', []):
#                 self.bullet_points.append(DummyBulletPoint(bp_text))
#
#         def _format_date(self, date_obj):
#             """Format date object to 'Mon YYYY' format"""
#             if not date_obj:
#                 return ""
#
#             if hasattr(date_obj, 'strftime'):
#                 return date_obj.strftime('%b %Y')
#             return str(date_obj)
#
#     class DummyEducation:
#         def __init__(self, data):
#             from datetime import datetime
#
#             self.school_name = data.get('school_name', '')
#             self.location = data.get('location', '')
#             self.degree = data.get('degree', '')
#             self.degree_type = data.get('degree_type', 'bachelor')
#             self.field_of_study = data.get('field_of_study', '')
#
#             # Process graduation date
#             grad_date_str = data.get('graduation_date', '')
#             if grad_date_str:
#                 try:
#                     date_obj = datetime.strptime(grad_date_str, '%Y-%m-%d').date()
#                     self.graduation_date = date_obj
#                 except (ValueError, TypeError):
#                     self.graduation_date = grad_date_str
#             else:
#                 self.graduation_date = None
#
#             self.formatted_graduation_date = self._format_date(self.graduation_date)
#             self.gpa = data.get('gpa', '')
#
#         def _format_date(self, date_obj):
#             """Format date object to 'Mon YYYY' format"""
#             if not date_obj:
#                 return ""
#
#             if hasattr(date_obj, 'strftime'):
#                 return date_obj.strftime('%b %Y')
#             return str(date_obj)
#
#     class DummyProject:
#         def __init__(self, data):
#             from datetime import datetime
#
#             self.project_name = data.get('project_name', '')
#             self.summary = data.get('summary', '')
#
#             # Process start date
#             start_date_str = data.get('start_date', '')
#             if start_date_str:
#                 try:
#                     date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#                     self.start_date = date_obj
#                 except (ValueError, TypeError):
#                     self.start_date = start_date_str
#             else:
#                 self.start_date = None
#
#             # Process completion date
#             completion_date_str = data.get('completion_date', '')
#             if completion_date_str:
#                 try:
#                     date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
#                     self.completion_date = date_obj
#                 except (ValueError, TypeError):
#                     self.completion_date = completion_date_str
#             else:
#                 self.completion_date = None
#
#             # Create formatted dates
#             self.formatted_start_date = self._format_date(self.start_date)
#             self.formatted_completion_date = self._format_date(self.completion_date)
#
#             # Create a date range string
#             if self.formatted_start_date and self.formatted_completion_date:
#                 self.date_range = f"{self.formatted_start_date} - {self.formatted_completion_date}"
#             elif self.formatted_start_date:
#                 self.date_range = f"{self.formatted_start_date} - Present"
#             else:
#                 self.date_range = ""
#
#             self.project_link = data.get('project_link', '')
#             self.github_link = data.get('github_link', '')
#             self.bullet_points = DummyQuerySet()
#
#             # Add bullet points
#             for bp_text in data.get('bullet_points', []):
#                 self.bullet_points.append(DummyBulletPoint(bp_text))
#
#         def _format_date(self, date_obj):
#             """Format date object to 'Mon YYYY' format"""
#             if not date_obj:
#                 return ""
#
#             if hasattr(date_obj, 'strftime'):
#                 return date_obj.strftime('%b %Y')
#             return str(date_obj)
#
#     class DummyCertification:
#         def __init__(self, data):
#             from datetime import datetime
#
#             self.name = data.get('name', '')
#             self.institute = data.get('institute', '')
#
#             # Process completion date
#             completion_date_str = data.get('completion_date', '')
#             if completion_date_str:
#                 try:
#                     date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
#                     self.completion_date = date_obj
#                 except (ValueError, TypeError):
#                     self.completion_date = completion_date_str
#             else:
#                 self.completion_date = None
#
#             # Process expiration date
#             expiration_date_str = data.get('expiration_date', '')
#             if expiration_date_str:
#                 try:
#                     date_obj = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
#                     self.expiration_date = date_obj
#                 except (ValueError, TypeError):
#                     self.expiration_date = expiration_date_str
#             else:
#                 self.expiration_date = None
#
#             # Create formatted dates
#             self.formatted_completion_date = self._format_date(self.completion_date)
#             self.formatted_expiration_date = self._format_date(self.expiration_date)
#
#             self.score = data.get('score', '')
#             self.link = data.get('link', '')
#             self.description = data.get('description', '')
#
#         def _format_date(self, date_obj):
#             """Format date object to 'Mon YYYY' format"""
#             if not date_obj:
#                 return ""
#
#             if hasattr(date_obj, 'strftime'):
#                 return date_obj.strftime('%b %Y')
#             return str(date_obj)
#
#     class DummyLanguage:
#         def __init__(self, data):
#             self.language_name = data.get('language_name', '')
#             self.proficiency = data.get('proficiency', 'basic')
#
#         def get_proficiency_display(self):
#             levels = {
#                 'basic': 'Basic',
#                 'intermediate': 'Intermediate',
#                 'advanced': 'Advanced',
#                 'native': 'Native'
#             }
#             return levels.get(self.proficiency, self.proficiency)
#
#     class DummyCustomData:
#         def __init__(self, data):
#             from datetime import datetime
#
#             self.name = data.get('name', '')
#
#             # Process completion date
#             completion_date_str = data.get('completion_date', '')
#             if completion_date_str:
#                 try:
#                     date_obj = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
#                     self.completion_date = date_obj
#                 except (ValueError, TypeError):
#                     self.completion_date = completion_date_str
#             else:
#                 self.completion_date = None
#
#             # Create formatted date
#             self.formatted_completion_date = self._format_date(self.completion_date)
#
#             self.bullet_points = data.get('bullet_points', '')
#             self.description = data.get('description', '')
#             self.link = data.get('link', '')
#             self.institution_name = data.get('institution_name', '')
#
#         def _format_date(self, date_obj):
#             """Format date object to 'Mon YYYY' format"""
#             if not date_obj:
#                 return ""
#
#             if hasattr(date_obj, 'strftime'):
#                 return date_obj.strftime('%b %Y')
#             return str(date_obj)
#
#     class DummyResume:
#         def __init__(self):
#             # Add personal info attributes
#             personal_info = form_data.get('personal_info', {})
#             self.first_name = personal_info.get('first_name', '')
#             self.mid_name = personal_info.get('mid_name', '')
#             self.last_name = personal_info.get('last_name', '')
#             self.full_name = f"{self.first_name} {self.mid_name} {self.last_name}".strip()
#             self.email = personal_info.get('email', '')
#             self.phone = personal_info.get('phone', '')
#             self.address = personal_info.get('address', '')
#             self.linkedin = personal_info.get('linkedin', '')
#             self.github = personal_info.get('github', '')
#             self.portfolio = personal_info.get('portfolio', '')
#
#             # Add summary
#             self.summary = form_data.get('summary', '')
#
#             # Initialize collections
#             self.skills = DummyQuerySet()
#             self.experiences = DummyQuerySet()
#             self.educations = DummyQuerySet()
#             self.projects = DummyQuerySet()
#             self.certifications = DummyQuerySet()
#             self.languages = DummyQuerySet()
#             self.custom_data = DummyQuerySet()
#
#             # Populate skills
#             for skill_data in form_data.get('skills', []):
#                 self.skills.append(DummySkill(skill_data))
#
#             # Populate experiences
#             for exp_data in form_data.get('experiences', []):
#                 self.experiences.append(DummyExperience(exp_data))
#
#             # Populate educations
#             for edu_data in form_data.get('educations', []):
#                 self.educations.append(DummyEducation(edu_data))
#
#             # Populate projects
#             for proj_data in form_data.get('projects', []):
#                 self.projects.append(DummyProject(proj_data))
#
#             # Populate certifications
#             for cert_data in form_data.get('certifications', []):
#                 self.certifications.append(DummyCertification(cert_data))
#
#             # Populate languages
#             for lang_data in form_data.get('languages', []):
#                 self.languages.append(DummyLanguage(lang_data))
#
#             # Populate custom data
#             for custom_data in form_data.get('custom_sections', []):
#                 self.custom_data.append(DummyCustomData(custom_data))
#
#     resume = DummyResume()
#
#     try:
#         # Use a more reliable template path that matches your project structure
#         return render(request, f'resumes/templates/template{template_id}.html', {
#             'resume': resume,
#             'is_preview': True
#         })
#     except Exception as e:
#         # Return error message
#         error_html = f"""
#         <div class="p-4 text-center">
#             <h4 class="text-red-500 font-bold mb-2">Error Rendering Template</h4>
#             <p class="text-gray-600 mb-2">There was a problem generating your resume preview:</p>
#             <div class="bg-gray-100 p-3 rounded text-left text-sm text-gray-700 mb-4">
#                 <code>{str(e)}</code>
#             </div>
#             <p class="text-sm text-gray-500">Template path attempted: resumes/templates/template{template_id}.html</p>
#         </div>
#         """
#         return HttpResponse(error_html)