from django.shortcuts import render

# File: job_portal/services/supporting_codes/resume_support_code.py
# Path: job_portal/services/supporting_codes/resume_support_code.py

from django.utils.translation import gettext_lazy as _

# No longer need to import Resume here for TEMPLATE_CHOICES,
# but might be needed if other functions in this file use the Resume model directly.
# from job_portal.models import Resume

# --- DEFINE TEMPLATE_CHOICES and METADATA HERE ---
# This list defines the valid template identifiers and their display names.
# The first element is the value stored in Resume.template_name,
# the second is for display (though 'name' in TEMPLATE_METADATA will usually override for display).
TEMPLATE_CHOICES = [
    ('template1', _('Classic Professional')),
    ('template2', _('Modern Minimalist')),
    ('template3', _('Creative Compact')),
    ('template4', _('Technical Focus')),
    ('template5', _('Elegant Executive')),
    ('template6', _('Academic & Research')),
    # Add more templates here if needed.
    # The 'id' in TEMPLATE_METADATA below must match the first element of these tuples.
]

# This dictionary maps the internal template IDs (from TEMPLATE_CHOICES above)
# to their display metadata.
TEMPLATE_METADATA = {
    'template1': {
        'name': _('Classic Professional'),
        'description': _('A timeless and clean format, widely accepted and ATS-friendly.'),
        'preview_image_path': 'img/templates/1.jpg',
        'tags': [_('Classic'), _('ATS-Friendly'), _('Formal'), _('Traditional')],
        'category': _('Traditional'),
    },
    'template2': {
        'name': _('Modern Minimalist'),
        'description': _('Sleek, contemporary design focusing on clarity and key achievements.'),
        'preview_image_path': 'img/templates/2.jpg',
        'tags': [_('Modern'), _('Minimalist'), _('Clean Design'), _('Contemporary')],
        'category': _('Modern'),
    },
    'template3': {
        'name': _('Creative Compact'),
        'description': _('A stylish and compact layout, great for creative fields or concise resumes.'),
        'preview_image_path': 'img/templates/3.jpg',
        'tags': [_('Creative'), _('Compact'), _('Visual'), _('Design-Focused')],
        'category': _('Creative'),
    },
    'template4': {
        'name': _('Technical Focus'),
        'description': _('Highlights technical skills, projects, and certifications prominently.'),
        'preview_image_path': 'img/templates/4.jpg',
        'tags': [_('Technical'), _('Skills-Focused'), _('IT'), _('Developer')],
        'category': _('Specialized')
    },
    'template5': {
        'name': _('Elegant Executive'),
        'description': _('A sophisticated and formal design, suitable for senior-level positions.'),
        'preview_image_path': 'img/templates/5.jpg',
        'tags': [_('Executive'), _('Formal'), _('Senior Level'), _('Professional')],
        'category': _('Professional')
    },
    'template6': {
        'name': _('Academic & Research'),
        'description': _('Emphasizes education, publications, research, and academic achievements.'),
        'preview_image_path': 'img/templates/6.jpg',
        'tags': [_('Academic'), _('Research'), _('CV'), _('Education-Focused')],
        'category': _('Academic')
    },
    # Add metadata for any other templates defined in TEMPLATE_CHOICES
}


def get_all_template_info():
    """
    Returns a list of dictionaries, each containing details for a resume template.
    The 'id' in each dictionary corresponds to the value to be stored in Resume.template_name.
    It iterates through the locally defined TEMPLATE_CHOICES.
    """
    all_info = []
    # MODIFIED: Iterate over TEMPLATE_CHOICES defined in this file
    for template_value, template_display_name_from_choice in TEMPLATE_CHOICES:
        metadata = TEMPLATE_METADATA.get(template_value, {})

        template_details = {
            'id': template_value,
            'name': metadata.get('name', template_display_name_from_choice),  # Use metadata name or fallback
            'description': metadata.get('description', _('A versatile template for your professional resume.')),
            'preview_image_path': metadata.get('preview_image_path', 'images/resume-previews/default.webp'),
            'tags': metadata.get('tags', []),
            'category': metadata.get('category', _('General')),
        }
        all_info.append(template_details)
    return all_info


def get_template_static_info(template_id):
    """
    Returns metadata for a single template by its ID using locally defined data.
    """
    display_name_from_choices = template_id
    for value, display_name in TEMPLATE_CHOICES:  # Use local TEMPLATE_CHOICES
        if value == template_id:
            display_name_from_choices = display_name
            break

    metadata = TEMPLATE_METADATA.get(template_id)
    if metadata:
        return {
            'id': template_id,
            'name': metadata.get('name', display_name_from_choices),
            'description': metadata.get('description', ''),
            'preview_image_path': metadata.get('preview_image_path', 'images/resume-previews/default.webp'),
            'tags': metadata.get('tags', []),
            'category': metadata.get('category', _('General')),
        }
    # Fallback if template_id is in TEMPLATE_CHOICES but not in TEMPLATE_METADATA
    elif any(choice[0] == template_id for choice in TEMPLATE_CHOICES):
        return {
            'id': template_id,
            'name': display_name_from_choices,
            'description': _('Standard resume template.'),
            'preview_image_path': 'images/resume-previews/default.webp',
            'tags': [],
            'category': _('General'),
        }
    return None

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

from datetime import date, datetime

# It's good practice to define these choice dictionaries once if they are shared
# or ensure they are consistent with your models.py choices.
# For this example, they are embedded in the Dummy classes.

def create_experienced_resume():
    """Create a sample resume for an experienced professional, matching models.py."""

    class DummyQuerySet(list):
        def exists(self):
            return len(self) > 0

        def all(self):
            return self

    class DummyKeywordTag:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

    class DummyExperienceBulletPoint:
        def __init__(self, bullet_text):
            self.bullet_text = bullet_text
            self.keywords = DummyQuerySet()

    class DummyProjectBulletPoint:
        def __init__(self, bullet_text):
            self.bullet_text = bullet_text
            self.keywords = DummyQuerySet()

    class DummyCustomSectionBulletPoint:
        def __init__(self, bullet_text):
            self.bullet_text = bullet_text

    class DummyPersonalInfo:
        def __init__(self):
            self.first_name = "Alex"
            self.middle_name = "J."
            self.last_name = "Morgan"
            self.email = "alex.morgan@example.com"
            self.phone_number = "(555) 123-4567"
            self.linkedin_url = "https://linkedin.com/in/alexmorgan"
            self.github_url = "https://github.com/alexmorgan"
            self.portfolio_url = "https://alexmorgan.dev"
            self.address_line1 = "123 Tech Avenue"
            self.address_line2 = "Suite 100"
            self.city = "Silicon Valley"
            self.state = "CA"
            self.zip_code = "94123"
            self.country = "USA"
            self.date_of_birth = date(1985, 7, 22)
            self.professional_summary = "Innovative full stack developer with 7+ years of experience building scalable web applications and leading high-performing development teams. Expertise in modern JavaScript frameworks, cloud architecture, and agile methodologies with a proven track record of delivering enterprise-level solutions that drive business growth and user engagement."
            self.profile_picture = None  # URL or path to a dummy image

        @property
        def full_name(self):
            parts = [self.first_name, self.middle_name, self.last_name]
            return " ".join(p for p in parts if p)

    class DummyExperience:
        def __init__(self, job_title, company_name, location, start_date, end_date=None, is_current_job=False,
                     description=""):
            self.job_title = job_title
            self.company_name = company_name
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.is_current_job = is_current_job
            self.description = description
            self.bullet_points = DummyQuerySet()

    class DummyEducation:
        def __init__(self, school_name, degree_name, field_of_study, education_level,  # Changed order to match model
                     location="", graduation_date=None, description="", gpa=None, start_date=None):
            self.school_name = school_name
            self.degree_name = degree_name
            self.field_of_study = field_of_study
            self.education_level = education_level
            self.location = location
            self.graduation_date = graduation_date
            self.start_date = start_date
            self.gpa = gpa  # Should be Decimal or float
            self.description = description

    class DummySkill:
        SKILL_CATEGORY_CHOICES = {  # Ensure these keys match your model's Skill.SKILL_CATEGORIES
            'technical': 'Technical', 'soft': 'Soft Skills', 'language': 'Programming Languages',
            'framework': 'Frameworks/Libraries', 'tool': 'Tools & Technologies', 'database': 'Databases',
            'cloud': 'Cloud Platforms', 'testing': 'Testing', 'devops': 'DevOps',
            'design': 'Design', 'project_management': 'Project Management', 'other_category': 'Other'
            # Matched 'other_category'
        }
        PROFICIENCY_LEVEL_CHOICES = {  # Ensure these keys match Skill.PROFICIENCY_LEVELS
            1: 'Novice', 2: 'Beginner', 3: 'Skillful', 4: 'Experienced', 5: 'Expert'
        }

        def __init__(self, skill_name, skill_category_choice, proficiency_level, custom_category_name=None):
            self.skill_name = skill_name
            self.skill_category_choice = skill_category_choice
            self.proficiency_level = proficiency_level  # Integer (e.g., 1-5)
            self.custom_category_name = custom_category_name if skill_category_choice == 'other_category' else None

        @property
        def effective_skill_category(self):
            if self.skill_category_choice == 'other_category' and self.custom_category_name:
                return self.custom_category_name
            return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice,
                                                   self.skill_category_choice.replace("_", " ").title())

        def get_skill_category_choice_display(self):
            return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice,
                                                   self.skill_category_choice.replace("_", " ").title())

        def get_proficiency_level_display(self):
            return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, "")

    class DummyProject:
        def __init__(self, project_name, description, start_date=None, end_date=None, project_url=None,
                     repository_url=None):
            self.project_name = project_name
            self.description = description
            self.start_date = start_date
            self.end_date = end_date
            self.project_url = project_url
            self.repository_url = repository_url
            self.bullet_points = DummyQuerySet()
            self.technologies_used = DummyQuerySet()  # List of DummySkill objects

    class DummyCertification:
        def __init__(self, certification_name, issuing_organization, issue_date=None, expiration_date=None,
                     description=None, credential_url=None, credential_id=None, score_percentage=None):
            self.certification_name = certification_name
            self.issuing_organization = issuing_organization
            self.issue_date = issue_date
            self.expiration_date = expiration_date
            self.description = description
            self.credential_url = credential_url
            self.credential_id = credential_id
            self.score_percentage = score_percentage  # Float/Decimal or None

    class DummyLanguage:
        PROFICIENCY_LEVEL_CHOICES = {  # Ensure these keys match Language.PROFICIENCY_LEVELS
            "native_fluent": "Native/Fluent",
            "advanced": "Advanced",
            "intermediate": "Intermediate",
            "basic": "Basic",
        }

        def __init__(self, language_name, proficiency_level):
            self.language_name = language_name
            self.proficiency_level = proficiency_level

        def get_proficiency_level_display(self):
            return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, self.proficiency_level.title())

    class DummyCustomSection:
        def __init__(self, section_title, institution_name=None, location=None, start_date=None, end_date=None,
                     description=None, section_url=None):
            self.section_title = section_title
            self.institution_name = institution_name
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.description = description
            self.section_url = section_url
            self.bullet_points = DummyQuerySet()

    class DummyResume:
        def __init__(self):
            self.id = 1
            self.title = "Senior Full Stack Developer Profile"
            self.personalinfo = DummyPersonalInfo()
            self.template_name = 'template1'
            self.slug = "alex-j-morgan-senior-full-stack-developer"
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            self.user = None  # Placeholder for user if needed, usually not for demo data structure

            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.skills = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_sections = DummyQuerySet()

        @property
        def full_name(self):
            return self.personalinfo.full_name if self.personalinfo else ""

    sample_resume = DummyResume()

    # Enhanced experiences with minimum 3 bullet points
    experiences_data = [
        {
            "job_title": "Senior Software Engineer", "company_name": "Tech Innovations Inc.",
            "location": "San Francisco, CA",
            "start_date": date(2020, 6, 1), "is_current_job": True,
            "description": "Led development of key product features and mentored junior engineers in a fast-paced startup environment.",
            "bullets": [
                "Led a team of 7 developers to deliver a cloud-based enterprise solution serving 50,000+ users, resulting in 35% increase in customer retention",
                "Implemented microservices architecture with Docker and Kubernetes, reducing deployment time by 60% and improving system scalability",
                "Architected and developed RESTful APIs using Node.js and Express.js, handling 10M+ requests per day with 99.9% uptime",
                "Mentored 5 junior developers through code reviews and pair programming sessions, improving team productivity by 25%",
                "Optimized database queries and implemented Redis caching, reducing average response time from 2.5s to 400ms"
            ]
        },
        {
            "job_title": "Lead Developer", "company_name": "Digital Solutions Ltd.", "location": "Seattle, WA",
            "start_date": date(2018, 3, 1), "end_date": date(2020, 5, 31),
            "description": "Managed a cross-functional team and oversaw complete project lifecycle for customer-facing applications.",
            "bullets": [
                "Designed and developed a customer portal using React and Node.js, increasing user engagement by 45% and reducing support tickets by 30%",
                "Collaborated with UX/UI designers to implement responsive design principles, ensuring compatibility across 15+ device types",
                "Established CI/CD pipelines using Jenkins and Git, reducing deployment errors by 80% and accelerating release cycles",
                "Integrated third-party payment systems (Stripe, PayPal) and security protocols, processing $2M+ in transactions monthly"
            ]
        },
        {
            "job_title": "Full Stack Developer", "company_name": "StartupTech Co.", "location": "Austin, TX",
            "start_date": date(2016, 8, 1), "end_date": date(2018, 2, 28),
            "description": "Developed and maintained web applications using modern JavaScript frameworks and backend technologies.",
            "bullets": [
                "Built and maintained 8+ web applications using React, Angular, and Vue.js, serving diverse client requirements",
                "Developed RESTful APIs with Python Django and Flask, managing complex business logic and data relationships",
                "Implemented automated testing suites using Jest and Pytest, achieving 90% code coverage and reducing bugs by 40%"
            ]
        }
    ]

    for exp_data in experiences_data:
        exp = DummyExperience(**{k: v for k, v in exp_data.items() if k != "bullets"})
        for bullet_text in exp_data["bullets"]:
            exp.bullet_points.append(DummyExperienceBulletPoint(bullet_text=bullet_text))
        sample_resume.experiences.append(exp)

    # Enhanced education with more details
    sample_resume.educations.extend([
        DummyEducation(
            school_name="University of Technology", degree_name="Master of Science", field_of_study="Computer Science",
            education_level="master", location="Boston, MA", graduation_date=date(2016, 5, 15), gpa=3.92,
            start_date=date(2014, 9, 1),
            description="Specialized in Software Engineering and Data Structures. Thesis on 'Scalable Web Architectures for High-Traffic Applications' with focus on microservices and cloud computing."
        ),
        DummyEducation(
            school_name="State University", degree_name="Bachelor of Science", field_of_study="Information Technology",
            education_level="bachelor", location="Austin, TX", graduation_date=date(2014, 5, 20), gpa=3.7,
            start_date=date(2010, 9, 1),
            description="Magna Cum Laude graduate. President of Computer Science Club, organized 5+ tech workshops and hackathons."
        )
    ])

    # Comprehensive skills list (15+ skills across different categories)
    skill_js = DummySkill(skill_name="JavaScript", skill_category_choice='language', proficiency_level=5)
    skill_python = DummySkill(skill_name="Python", skill_category_choice='language', proficiency_level=5)
    skill_typescript = DummySkill(skill_name="TypeScript", skill_category_choice='language', proficiency_level=4)
    skill_java = DummySkill(skill_name="Java", skill_category_choice='language', proficiency_level=4)

    skill_react = DummySkill(skill_name="React", skill_category_choice='framework', proficiency_level=5)
    skill_node = DummySkill(skill_name="Node.js", skill_category_choice='framework', proficiency_level=5)
    skill_django = DummySkill(skill_name="Django", skill_category_choice='framework', proficiency_level=4)
    skill_express = DummySkill(skill_name="Express.js", skill_category_choice='framework', proficiency_level=4)
    skill_angular = DummySkill(skill_name="Angular", skill_category_choice='framework', proficiency_level=3)

    skill_postgresql = DummySkill(skill_name="PostgreSQL", skill_category_choice='database', proficiency_level=4)
    skill_mongodb = DummySkill(skill_name="MongoDB", skill_category_choice='database', proficiency_level=4)
    skill_redis = DummySkill(skill_name="Redis", skill_category_choice='database', proficiency_level=3)

    skill_aws = DummySkill(skill_name="AWS", skill_category_choice='cloud', proficiency_level=4)
    skill_docker = DummySkill(skill_name="Docker", skill_category_choice='devops', proficiency_level=4)
    skill_kubernetes = DummySkill(skill_name="Kubernetes", skill_category_choice='devops', proficiency_level=3)

    skill_git = DummySkill(skill_name="Git", skill_category_choice='tool', proficiency_level=5)
    skill_jest = DummySkill(skill_name="Jest", skill_category_choice='testing', proficiency_level=4)

    skill_leadership = DummySkill(skill_name="Team Leadership", skill_category_choice='soft', proficiency_level=5)
    skill_agile = DummySkill(skill_name="Agile Methodologies", skill_category_choice='project_management',
                             proficiency_level=4)
    skill_communication = DummySkill(skill_name="Technical Communication", skill_category_choice='soft',
                                     proficiency_level=5)

    sample_resume.skills.extend([
        skill_js, skill_python, skill_typescript, skill_java,
        skill_react, skill_node, skill_django, skill_express, skill_angular,
        skill_postgresql, skill_mongodb, skill_redis,
        skill_aws, skill_docker, skill_kubernetes,
        skill_git, skill_jest,
        skill_leadership, skill_agile, skill_communication
    ])

    # Enhanced projects with more bullet points
    projects_data = [
        {
            "project_name": "E-commerce Analytics Dashboard",
            "description": "A comprehensive web application that visualizes sales data and provides actionable business insights for e-commerce platforms.",
            "start_date": date(2022, 3, 1), "end_date": date(2022, 8, 15),
            "project_url": "https://dashboard-demo.example.com",
            "repository_url": "https://github.com/example/analytics-dashboard",
            "bullets": [
                "Designed and implemented interactive data visualizations using D3.js and Chart.js, displaying real-time sales metrics for 500+ products",
                "Built responsive dashboard interface with React and Material-UI, supporting mobile and desktop viewing for executive stakeholders",
                "Integrated with multiple data sources including PostgreSQL, MongoDB, and external APIs, processing 1M+ data points daily",
                "Implemented real-time notifications and automated report generation, reducing manual reporting time by 70%"
            ],
            "technologies": [skill_react, skill_node, skill_postgresql]
        },
        {
            "project_name": "Microservices Task Management System",
            "description": "A distributed task management platform built with microservices architecture to handle enterprise-level project coordination.",
            "start_date": date(2021, 6, 1), "end_date": date(2021, 11, 30),
            "repository_url": "https://github.com/example/task-management",
            "bullets": [
                "Architected microservices using Docker containers and Kubernetes orchestration, supporting 10,000+ concurrent users",
                "Developed event-driven communication between services using Apache Kafka, ensuring 99.5% message delivery reliability",
                "Implemented OAuth 2.0 authentication and role-based access control, securing sensitive project data across multiple tenants"
            ],
            "technologies": [skill_docker, skill_kubernetes, skill_node]
        }
    ]

    for proj_data in projects_data:
        proj = DummyProject(**{k: v for k, v in proj_data.items() if k not in ["bullets", "technologies"]})
        for bullet_text in proj_data["bullets"]:
            proj.bullet_points.append(DummyProjectBulletPoint(bullet_text=bullet_text))
        if "technologies" in proj_data:
            proj.technologies_used.extend(proj_data["technologies"])
        sample_resume.projects.append(proj)

    # Enhanced certifications
    sample_resume.certifications.extend([
        DummyCertification(
            certification_name="AWS Certified Solutions Architect - Professional",
            issuing_organization="Amazon Web Services",
            issue_date=date(2022, 4, 10), expiration_date=date(2025, 4, 10),
            description="Validates expertise in designing distributed systems on AWS cloud platform with high availability and fault tolerance.",
            credential_url="https://aws.amazon.com/certification/certified-solutions-architect-professional/",
            credential_id="AWS-CSAP-12345", score_percentage=95.0
        ),
        DummyCertification(
            certification_name="Certified Kubernetes Administrator (CKA)",
            issuing_organization="Cloud Native Computing Foundation",
            issue_date=date(2021, 9, 15), expiration_date=date(2024, 9, 15),
            description="Demonstrates skills in Kubernetes cluster administration, networking, and troubleshooting.",
            credential_id="CKA-2021-001", score_percentage=88.0
        ),
        DummyCertification(
            certification_name="Professional Scrum Master I (PSM I)", issuing_organization="Scrum.org",
            issue_date=date(2020, 3, 20),
            description="Validates understanding of Scrum framework and ability to apply it effectively in real-world scenarios.",
            credential_id="PSM-001-2020", score_percentage=92.0
        )
    ])

    # Enhanced languages
    sample_resume.languages.extend([
        DummyLanguage(language_name="English", proficiency_level="native_fluent"),
        DummyLanguage(language_name="Spanish", proficiency_level="advanced"),
        DummyLanguage(language_name="French", proficiency_level="intermediate"),
    ])

    # Enhanced custom sections with more bullet points
    custom_sections_data = [
        {
            "section_title": "Volunteer Experience", "institution_name": "Code for Good",
            "location": "San Francisco, CA",
            "start_date": date(2019, 1, 1), "end_date": date(2022, 8, 1),
            "description": "Volunteered to develop web applications for non-profit organizations and community initiatives.",
            "section_url": "https://codeforgood.example.org",
            "bullets": [
                "Developed a donation tracking system for local food bank, increasing donation transparency and volunteer coordination efficiency by 40%",
                "Led a team of 8 volunteer developers to create a mentorship platform connecting 200+ students with industry professionals",
                "Organized monthly coding workshops for underrepresented communities, training 150+ individuals in web development fundamentals"
            ]
        },
        {
            "section_title": "Speaking & Publications", "institution_name": "Tech Conference Circuit",
            "location": "Various",
            "start_date": date(2020, 1, 1), "end_date": date(2023, 12, 31),
            "description": "Active speaker at technology conferences and contributor to technical publications.",
            "bullets": [
                "Delivered keynote presentation 'Scaling Microservices in the Cloud' at TechCon 2022, reaching 500+ attendees",
                "Published 3 technical articles on Medium about React performance optimization, garnering 10,000+ reads",
                "Conducted workshops on modern JavaScript frameworks at 5+ regional developer meetups"
            ]
        }
    ]

    for cs_data in custom_sections_data:
        cs = DummyCustomSection(**{k: v for k, v in cs_data.items() if k != "bullets"})
        for bullet_text in cs_data.get("bullets", []):
            cs.bullet_points.append(DummyCustomSectionBulletPoint(bullet_text=bullet_text))
        sample_resume.custom_sections.append(cs)

    return sample_resume


def create_fresher_resume():
    """Create a sample resume for a fresh graduate, matching models.py."""

    class DummyQuerySet(list):
        def exists(self): return len(self) > 0

        def all(self): return self

    class DummyKeywordTag:
        def __init__(self, name): self.name = name

        def __str__(self): return self.name

    class DummyExperienceBulletPoint:
        def __init__(self, bullet_text):
            self.bullet_text = bullet_text
            self.keywords = DummyQuerySet()

    class DummyProjectBulletPoint:
        def __init__(self, bullet_text):
            self.bullet_text = bullet_text
            self.keywords = DummyQuerySet()

    class DummyCustomSectionBulletPoint:
        def __init__(self, bullet_text):
            self.bullet_text = bullet_text

    class DummyPersonalInfo:
        def __init__(self):
            self.first_name = "Jamie"
            self.middle_name = ""
            self.last_name = "Taylor"
            self.email = "jamie.taylor@example.com"
            self.phone_number = "(555) 987-6543"
            self.linkedin_url = "https://linkedin.com/in/jamietaylor"
            self.github_url = "https://github.com/jamietaylor"
            self.portfolio_url = "https://jamietaylor.dev"
            self.address_line1 = "123 University Ave"
            self.address_line2 = ""
            self.city = "Boston"
            self.state = "MA"
            self.zip_code = "02215"
            self.country = "USA"
            self.date_of_birth = date(2001, 3, 15)
            self.professional_summary = "Recent Computer Science graduate with strong foundations in programming, software development, and data structures. Passionate about creating innovative solutions and experienced in full-stack development through academic projects and internships. Eager to contribute to a dynamic development team while continuing to grow technical expertise in modern web technologies and agile methodologies."
            self.profile_picture = None

        @property
        def full_name(self):
            parts = [self.first_name, self.middle_name, self.last_name]
            return " ".join(p for p in parts if p)

    class DummyExperience:
        def __init__(self, job_title, company_name, location, start_date, end_date=None, is_current_job=False,
                     description=""):
            self.job_title = job_title
            self.company_name = company_name
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.is_current_job = is_current_job
            self.description = description
            self.bullet_points = DummyQuerySet()

    class DummyEducation:
        def __init__(self, school_name, degree_name, field_of_study, education_level,
                     location="", graduation_date=None, description="", gpa=None, start_date=None):
            self.school_name = school_name
            self.degree_name = degree_name
            self.field_of_study = field_of_study
            self.education_level = education_level
            self.location = location
            self.graduation_date = graduation_date
            self.start_date = start_date
            self.gpa = gpa
            self.description = description

    class DummySkill:
        SKILL_CATEGORY_CHOICES = {
            'technical': 'Technical', 'soft': 'Soft Skills', 'language': 'Programming Languages',
            'framework': 'Frameworks/Libraries', 'tool': 'Tools & Technologies', 'database': 'Databases',
            'cloud': 'Cloud Platforms', 'testing': 'Testing', 'devops': 'DevOps',
            'design': 'Design', 'project_management': 'Project Management', 'other_category': 'Other'
        }
        PROFICIENCY_LEVEL_CHOICES = {
            1: 'Novice', 2: 'Beginner', 3: 'Skillful', 4: 'Experienced', 5: 'Expert'
        }

        def __init__(self, skill_name, skill_category_choice, proficiency_level, custom_category_name=None):
            self.skill_name = skill_name
            self.skill_category_choice = skill_category_choice
            self.proficiency_level = proficiency_level
            self.custom_category_name = custom_category_name if skill_category_choice == 'other_category' else None

        @property
        def effective_skill_category(self):
            if self.skill_category_choice == 'other_category' and self.custom_category_name:
                return self.custom_category_name
            return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice,
                                                   self.skill_category_choice.replace("_", " ").title())

        def get_skill_category_choice_display(self):
            return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice,
                                                   self.skill_category_choice.replace("_", " ").title())

        def get_proficiency_level_display(self):
            return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, "")

    class DummyProject:
        def __init__(self, project_name, description, start_date=None, end_date=None, project_url=None,
                     repository_url=None):
            self.project_name = project_name
            self.description = description
            self.start_date = start_date
            self.end_date = end_date
            self.project_url = project_url
            self.repository_url = repository_url
            self.bullet_points = DummyQuerySet()
            self.technologies_used = DummyQuerySet()

    class DummyCertification:
        def __init__(self, certification_name, issuing_organization, issue_date=None, expiration_date=None,
                     description=None, credential_url=None, credential_id=None, score_percentage=None):
            self.certification_name = certification_name
            self.issuing_organization = issuing_organization
            self.issue_date = issue_date
            self.expiration_date = expiration_date
            self.description = description
            self.credential_url = credential_url
            self.credential_id = credential_id
            self.score_percentage = score_percentage

    class DummyLanguage:
        PROFICIENCY_LEVEL_CHOICES = {
            "native_fluent": "Native/Fluent", "advanced": "Advanced",
            "intermediate": "Intermediate", "basic": "Basic",
        }

        def __init__(self, language_name, proficiency_level):
            self.language_name = language_name
            self.proficiency_level = proficiency_level

        def get_proficiency_level_display(self):
            return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, self.proficiency_level.title())

    class DummyCustomSection:
        def __init__(self, section_title, institution_name=None, location=None, start_date=None, end_date=None,
                     description=None, section_url=None):
            self.section_title = section_title
            self.institution_name = institution_name
            self.location = location
            self.start_date = start_date
            self.end_date = end_date
            self.description = description
            self.section_url = section_url
            self.bullet_points = DummyQuerySet()

    class DummyResume:
        def __init__(self):
            self.id = 2
            self.title = "Computer Science Graduate Profile"
            self.personalinfo = DummyPersonalInfo()
            self.template_name = 'template2'
            self.slug = "jamie-taylor-computer-science-graduate"
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            self.user = None

            self.experiences = DummyQuerySet()
            self.educations = DummyQuerySet()
            self.skills = DummyQuerySet()
            self.projects = DummyQuerySet()
            self.certifications = DummyQuerySet()
            self.languages = DummyQuerySet()
            self.custom_sections = DummyQuerySet()

        @property
        def full_name(self):
            return self.personalinfo.full_name if self.personalinfo else ""

    fresher_resume = DummyResume()

    # Enhanced education section
    fresher_resume.educations.extend([
        DummyEducation(
            school_name="Boston University", degree_name="Bachelor of Science", field_of_study="Computer Science",
            education_level="bachelor", location="Boston, MA", graduation_date=date(2023, 5, 15), gpa=3.8,
            start_date=date(2019, 9, 1),
            description="Summa Cum Laude graduate. Dean's List for 6 semesters. Senior Capstone Project: Machine Learning-based Recommendation System. Active member of ACM Student Chapter and Programming Club."
        )
    ])

    # Enhanced internship and part-time experience with 3+ bullet points
    experiences_data = [
        {
            "job_title": "Software Development Intern", "company_name": "TechStart Solutions", "location": "Boston, MA",
            "start_date": date(2022, 6, 1), "end_date": date(2022, 8, 31),
            "description": "Collaborated with senior developers to build and test new features for e-commerce platform.",
            "bullets": [
                "Assisted in developing features for an e-commerce platform using React.js and Node.js, contributing to 15% increase in user engagement",
                "Participated in daily scrum meetings and sprint planning sessions, learning agile development methodologies and project management",
                "Wrote and executed unit tests using Jest framework, achieving 85% code coverage for assigned modules",
                "Collaborated with QA team to identify and fix 20+ bugs, improving overall application stability"
            ]
        },
        {
            "job_title": "Part-time Web Developer", "company_name": "University IT Department",
            "location": "Boston, MA",
            "start_date": date(2021, 9, 1), "end_date": date(2022, 5, 31),
            "description": "Developed and maintained university department websites and internal tools.",
            "bullets": [
                "Built responsive websites for 3 university departments using HTML, CSS, JavaScript, and WordPress CMS",
                "Created automated scripts in Python to process student data, reducing manual data entry time by 60%",
                "Provided technical support to faculty and staff, resolving 50+ IT issues and maintaining documentation"
            ]
        }
    ]

    for exp_data in experiences_data:
        exp = DummyExperience(**{k: v for k, v in exp_data.items() if k != "bullets"})
        for bullet_text in exp_data["bullets"]:
            exp.bullet_points.append(DummyExperienceBulletPoint(bullet_text=bullet_text))
        fresher_resume.experiences.append(exp)

    # Comprehensive skills for fresher (12+ skills)
    skill_java_f = DummySkill(skill_name="Java", skill_category_choice='language', proficiency_level=4)
    skill_python_f = DummySkill(skill_name="Python", skill_category_choice='language', proficiency_level=4)
    skill_javascript_f = DummySkill(skill_name="JavaScript", skill_category_choice='language', proficiency_level=3)
    skill_cpp_f = DummySkill(skill_name="C++", skill_category_choice='language', proficiency_level=3)
    skill_html_css_f = DummySkill(skill_name="HTML/CSS", skill_category_choice='language', proficiency_level=4)

    skill_react_f = DummySkill(skill_name="React", skill_category_choice='framework', proficiency_level=3)
    skill_django_f = DummySkill(skill_name="Django", skill_category_choice='framework', proficiency_level=3)
    skill_node_f = DummySkill(skill_name="Node.js", skill_category_choice='framework', proficiency_level=2)
    skill_spring_f = DummySkill(skill_name="Spring Boot", skill_category_choice='framework', proficiency_level=2)

    skill_mysql_f = DummySkill(skill_name="MySQL", skill_category_choice='database', proficiency_level=3)
    skill_postgresql_f = DummySkill(skill_name="PostgreSQL", skill_category_choice='database', proficiency_level=3)

    skill_git_f = DummySkill(skill_name="Git", skill_category_choice='tool', proficiency_level=4)
    skill_vs_code_f = DummySkill(skill_name="VS Code", skill_category_choice='tool', proficiency_level=4)
    skill_postman_f = DummySkill(skill_name="Postman", skill_category_choice='tool', proficiency_level=3)

    skill_problem_solving_f = DummySkill(skill_name="Problem Solving", skill_category_choice='soft',
                                         proficiency_level=4)
    skill_teamwork_f = DummySkill(skill_name="Team Collaboration", skill_category_choice='soft', proficiency_level=4)
    skill_communication_f = DummySkill(skill_name="Communication", skill_category_choice='soft', proficiency_level=4)

    fresher_resume.skills.extend([
        skill_java_f, skill_python_f, skill_javascript_f, skill_cpp_f, skill_html_css_f,
        skill_react_f, skill_django_f, skill_node_f, skill_spring_f,
        skill_mysql_f, skill_postgresql_f,
        skill_git_f, skill_vs_code_f, skill_postman_f,
        skill_problem_solving_f, skill_teamwork_f, skill_communication_f
    ])

    # Enhanced projects with 3+ bullet points each
    projects_data = [
        {
            "project_name": "Student Management System",
            "description": "A comprehensive web application for managing student records, course enrollment, and academic progress tracking.",
            "start_date": date(2022, 9, 1), "end_date": date(2023, 4, 30),
            "repository_url": "https://github.com/jamietaylor/student-ms",
            "bullets": [
                "Designed and implemented a full-stack web application using Django REST framework and React.js, managing data for 500+ student records",
                "Developed responsive user interface with modern UI/UX principles, ensuring seamless experience across desktop and mobile devices",
                "Created comprehensive database schema with PostgreSQL, implementing relationships between students, courses, and enrollment data",
                "Integrated authentication and authorization system with role-based access control for students, faculty, and administrators"
            ],
            "technologies": [skill_react_f, skill_django_f, skill_postgresql_f]
        },
        {
            "project_name": "Personal Finance Tracker",
            "description": "A mobile-responsive web application for tracking personal expenses, income, and generating financial reports.",
            "start_date": date(2022, 2, 1), "end_date": date(2022, 5, 31),
            "repository_url": "https://github.com/jamietaylor/finance-tracker",
            "bullets": [
                "Built interactive dashboard using Chart.js and D3.js to visualize spending patterns and financial trends over time",
                "Implemented RESTful API with Node.js and Express.js, handling CRUD operations for financial transactions and categories",
                "Designed secure user authentication system with JWT tokens and password encryption using bcrypt library"
            ],
            "technologies": [skill_javascript_f, skill_node_f, skill_mysql_f]
        },
        {
            "project_name": "Campus Event Management System",
            "description": "A collaborative platform for university students to create, manage, and participate in campus events and activities.",
            "start_date": date(2021, 10, 1), "end_date": date(2022, 1, 31),
            "repository_url": "https://github.com/jamietaylor/campus-events",
            "bullets": [
                "Developed event creation and management features using Java Spring Boot framework with MVC architecture",
                "Implemented real-time notifications and messaging system using WebSocket technology for event updates",
                "Created responsive front-end interface with Bootstrap framework, supporting event browsing and RSVP functionality"
            ],
            "technologies": [skill_java_f, skill_spring_f, skill_mysql_f]
        }
    ]

    for proj_data in projects_data:
        proj = DummyProject(**{k: v for k, v in proj_data.items() if k not in ["bullets", "technologies"]})
        for bullet_text in proj_data["bullets"]:
            proj.bullet_points.append(DummyProjectBulletPoint(bullet_text=bullet_text))
        if "technologies" in proj_data:
            proj.technologies_used.extend(proj_data["technologies"])
        fresher_resume.projects.append(proj)

    # Enhanced certifications for fresher
    fresher_resume.certifications.extend([
        DummyCertification(
            certification_name="Oracle Certified Associate, Java SE 8 Programmer", issuing_organization="Oracle",
            issue_date=date(2022, 11, 10), credential_id="OCAJP-001", score_percentage=85.0,
            description="Validates foundational knowledge of Java programming language and object-oriented programming principles."
        ),
        DummyCertification(
            certification_name="AWS Certified Cloud Practitioner", issuing_organization="Amazon Web Services",
            issue_date=date(2023, 2, 15), expiration_date=date(2026, 2, 15),
            credential_id="AWS-CCP-2023", score_percentage=78.0,
            description="Demonstrates overall understanding of AWS cloud services and basic architectural principles."
        ),
        DummyCertification(
            certification_name="Google IT Support Professional Certificate", issuing_organization="Google via Coursera",
            issue_date=date(2021, 8, 20), credential_id="GOOGLE-IT-001",
            description="Comprehensive training in troubleshooting, customer service, networking, operating systems, and system administration."
        )
    ])

    # Enhanced languages
    fresher_resume.languages.extend([
        DummyLanguage(language_name="English", proficiency_level="native_fluent"),
        DummyLanguage(language_name="Spanish", proficiency_level="intermediate"),
    ])

    # Enhanced custom sections with 3+ bullet points
    custom_sections_data = [
        {
            "section_title": "Extracurricular Activities", "institution_name": "Boston University Coding Club",
            "location": "Boston, MA", "start_date": date(2021, 9, 1), "end_date": date(2023, 5, 1),
            "description": "Active member and event organizer for university's premier programming organization.",
            "bullets": [
                "Organized weekly coding workshops and tutorial sessions for 50+ students, covering topics from basic programming to advanced algorithms",
                "Participated in National Hackathon 2022, developing a health monitoring app that placed 3rd out of 150+ teams",
                "Led a team of 6 students in ACM Programming Contest, achieving regional qualification and improving problem-solving skills",
                "Mentored 15+ freshman students in programming fundamentals and career guidance through peer tutoring program"
            ]
        },
        {
            "section_title": "Academic Achievements", "institution_name": "Boston University",
            "location": "Boston, MA", "start_date": date(2019, 9, 1), "end_date": date(2023, 5, 1),
            "description": "Recognition for academic excellence and leadership in computer science program.",
            "bullets": [
                "Dean's List recipient for 6 consecutive semesters, maintaining GPA above 3.7 throughout undergraduate studies",
                "Received 'Outstanding Student in Computer Science' award for senior capstone project on machine learning applications",
                "Teaching Assistant for Data Structures and Algorithms course, helping 80+ students understand complex programming concepts"
            ]
        },
        {
            "section_title": "Volunteer Work", "institution_name": "Code for Community",
            "location": "Boston, MA", "start_date": date(2020, 6, 1), "end_date": date(2023, 4, 1),
            "description": "Volunteer developer contributing to open-source projects for local non-profit organizations.",
            "bullets": [
                "Developed a volunteer scheduling website for local animal shelter, streamlining coordination for 200+ volunteers",
                "Created educational programming content for underserved youth, teaching basic coding skills to 30+ middle school students",
                "Participated in monthly community coding meetups, collaborating on civic technology projects and digital literacy initiatives"
            ]
        }
    ]

    for cs_data in custom_sections_data:
        cs = DummyCustomSection(**{k: v for k, v in cs_data.items() if k != "bullets"})
        for bullet_text in cs_data.get("bullets", []):
            cs.bullet_points.append(DummyCustomSectionBulletPoint(bullet_text=bullet_text))
        fresher_resume.custom_sections.append(cs)

    return fresher_resume
# def create_experienced_resume():
#     """Create a sample resume for an experienced professional, matching models.py."""
#
#     class DummyQuerySet(list):
#         def exists(self):
#             return len(self) > 0
#         def all(self):
#             return self
#
#     class DummyKeywordTag:
#         def __init__(self, name):
#             self.name = name
#         def __str__(self):
#             return self.name
#
#     class DummyExperienceBulletPoint:
#         def __init__(self, bullet_text):
#             self.bullet_text = bullet_text
#             self.keywords = DummyQuerySet()
#
#     class DummyProjectBulletPoint:
#         def __init__(self, bullet_text):
#             self.bullet_text = bullet_text
#             self.keywords = DummyQuerySet()
#
#     class DummyCustomSectionBulletPoint:
#         def __init__(self, bullet_text):
#             self.bullet_text = bullet_text
#
#     class DummyPersonalInfo:
#         def __init__(self):
#             self.first_name = "Alex"
#             self.middle_name = "J."
#             self.last_name = "Morgan"
#             self.email = "alex.morgan@example.com"
#             self.phone_number = "(555) 123-4567"
#             self.linkedin_url = "https://linkedin.com/in/alexmorgan"
#             self.github_url = "https://github.com/alexmorgan"
#             self.portfolio_url = "https://alexmorgan.dev"
#             self.address_line1 = "123 Tech Avenue"
#             self.address_line2 = "Suite 100"
#             self.city = "Silicon Valley"
#             self.state = "CA"
#             self.zip_code = "94123"
#             self.country = "USA"
#             self.date_of_birth = date(1985, 7, 22)
#             self.professional_summary = "Innovative full stack developer with 7+ years of experience..."
#             self.profile_picture = None # URL or path to a dummy image
#
#         @property
#         def full_name(self):
#             parts = [self.first_name, self.middle_name, self.last_name]
#             return " ".join(p for p in parts if p)
#
#     class DummyExperience:
#         def __init__(self, job_title, company_name, location, start_date, end_date=None, is_current_job=False, description=""):
#             self.job_title = job_title
#             self.company_name = company_name
#             self.location = location
#             self.start_date = start_date
#             self.end_date = end_date
#             self.is_current_job = is_current_job
#             self.description = description
#             self.bullet_points = DummyQuerySet()
#
#     class DummyEducation:
#         def __init__(self, school_name, degree_name, field_of_study, education_level, # Changed order to match model
#                      location="", graduation_date=None, description="", gpa=None, start_date=None):
#             self.school_name = school_name
#             self.degree_name = degree_name
#             self.field_of_study = field_of_study
#             self.education_level = education_level
#             self.location = location
#             self.graduation_date = graduation_date
#             self.start_date = start_date
#             self.gpa = gpa # Should be Decimal or float
#             self.description = description
#
#     class DummySkill:
#         SKILL_CATEGORY_CHOICES = { # Ensure these keys match your model's Skill.SKILL_CATEGORIES
#             'technical': 'Technical', 'soft': 'Soft Skills', 'language': 'Programming Languages',
#             'framework': 'Frameworks/Libraries', 'tool': 'Tools & Technologies', 'database': 'Databases',
#             'cloud': 'Cloud Platforms', 'testing': 'Testing', 'devops': 'DevOps',
#             'design': 'Design', 'project_management': 'Project Management', 'other_category': 'Other' # Matched 'other_category'
#         }
#         PROFICIENCY_LEVEL_CHOICES = { # Ensure these keys match Skill.PROFICIENCY_LEVELS
#             1: 'Novice', 2: 'Beginner', 3: 'Skillful', 4: 'Experienced', 5: 'Expert'
#         }
#         def __init__(self, skill_name, skill_category_choice, proficiency_level, custom_category_name=None):
#             self.skill_name = skill_name
#             self.skill_category_choice = skill_category_choice
#             self.proficiency_level = proficiency_level # Integer (e.g., 1-5)
#             self.custom_category_name = custom_category_name if skill_category_choice == 'other_category' else None
#
#         @property
#         def effective_skill_category(self):
#             if self.skill_category_choice == 'other_category' and self.custom_category_name:
#                 return self.custom_category_name
#             return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice, self.skill_category_choice.replace("_", " ").title())
#
#         def get_skill_category_choice_display(self):
#              return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice, self.skill_category_choice.replace("_", " ").title())
#
#         def get_proficiency_level_display(self):
#             return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, "")
#
#
#     class DummyProject:
#         def __init__(self, project_name, description, start_date=None, end_date=None, project_url=None, repository_url=None):
#             self.project_name = project_name
#             self.description = description
#             self.start_date = start_date
#             self.end_date = end_date
#             self.project_url = project_url
#             self.repository_url = repository_url
#             self.bullet_points = DummyQuerySet()
#             self.technologies_used = DummyQuerySet() # List of DummySkill objects
#
#     class DummyCertification:
#         def __init__(self, certification_name, issuing_organization, issue_date=None, expiration_date=None, description=None, credential_url=None, credential_id=None, score_percentage=None):
#             self.certification_name = certification_name
#             self.issuing_organization = issuing_organization
#             self.issue_date = issue_date
#             self.expiration_date = expiration_date
#             self.description = description
#             self.credential_url = credential_url
#             self.credential_id = credential_id
#             self.score_percentage = score_percentage # Float/Decimal or None
#
#     class DummyLanguage:
#         PROFICIENCY_LEVEL_CHOICES = { # Ensure these keys match Language.PROFICIENCY_LEVELS
#             "native_fluent": "Native/Fluent",
#             "advanced": "Advanced",
#             "intermediate": "Intermediate",
#             "basic": "Basic",
#         }
#         def __init__(self, language_name, proficiency_level):
#             self.language_name = language_name
#             self.proficiency_level = proficiency_level
#
#         def get_proficiency_level_display(self):
#             return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, self.proficiency_level.title())
#
#     class DummyCustomSection:
#         def __init__(self, section_title, institution_name=None, location=None, start_date=None, end_date=None, description=None, section_url=None):
#             self.section_title = section_title
#             self.institution_name = institution_name
#             self.location = location
#             self.start_date = start_date
#             self.end_date = end_date
#             self.description = description
#             self.section_url = section_url
#             self.bullet_points = DummyQuerySet()
#
#     class DummyResume:
#         def __init__(self):
#             self.id = 1
#             self.title = "Senior Full Stack Developer Profile"
#             self.personalinfo = DummyPersonalInfo()
#             self.template_name = 'template1'
#             self.slug = "alex-j-morgan-senior-full-stack-developer"
#             self.created_at = datetime.now()
#             self.updated_at = datetime.now()
#             self.user = None # Placeholder for user if needed, usually not for demo data structure
#
#             self.experiences = DummyQuerySet()
#             self.educations = DummyQuerySet()
#             self.skills = DummyQuerySet()
#             self.projects = DummyQuerySet()
#             self.certifications = DummyQuerySet()
#             self.languages = DummyQuerySet()
#             self.custom_sections = DummyQuerySet()
#
#         @property
#         def full_name(self):
#             return self.personalinfo.full_name if self.personalinfo else ""
#
#     sample_resume = DummyResume()
#
#     experiences_data = [
#         {
#             "job_title": "Senior Software Engineer", "company_name": "Tech Innovations Inc.", "location": "San Francisco, CA",
#             "start_date": date(2020, 6, 1), "is_current_job": True,
#             "description": "Led development of key product features and mentored junior engineers.",
#             "bullets": [
#                 "Led a team of 7 developers to deliver a cloud-based enterprise solution...",
#                 "Implemented microservices architecture with Docker and Kubernetes...",
#             ]
#         },
#         {
#             "job_title": "Lead Developer", "company_name": "Digital Solutions Ltd.", "location": "Seattle, WA",
#             "start_date": date(2018, 3, 1), "end_date": date(2020, 5, 31),
#             "description": "Managed a team and oversaw project lifecycle for a new customer portal.",
#             "bullets": ["Designed and developed a customer portal using React and Node.js..."]
#         },
#     ]
#     for exp_data in experiences_data:
#         exp = DummyExperience(**{k:v for k,v in exp_data.items() if k!= "bullets"})
#         for bullet_text in exp_data["bullets"]:
#             exp.bullet_points.append(DummyExperienceBulletPoint(bullet_text=bullet_text))
#         sample_resume.experiences.append(exp)
#
#     sample_resume.educations.extend([
#         DummyEducation(
#             school_name="University of Technology", degree_name="Master of Science", field_of_study="Computer Science",
#             education_level="master", location="Boston, MA", graduation_date=date(2016, 5, 15), gpa=3.92,
#             start_date=date(2014, 9, 1), description="Thesis on Scalable Web Architectures."
#         ),
#     ])
#
#     # Define some skills to reference in projects
#     skill_js = DummySkill(skill_name="JavaScript", skill_category_choice='language', proficiency_level=5)
#     skill_python = DummySkill(skill_name="Python", skill_category_choice='language', proficiency_level=5)
#     skill_react = DummySkill(skill_name="React", skill_category_choice='framework', proficiency_level=4)
#     skill_node = DummySkill(skill_name="Node.js", skill_category_choice='framework', proficiency_level=4)
#     skill_django = DummySkill(skill_name="Django", skill_category_choice='framework', proficiency_level=4)
#     skill_leader = DummySkill(skill_name="Team Leadership", skill_category_choice='soft', proficiency_level=5)
#
#     sample_resume.skills.extend([skill_js, skill_python, skill_react, skill_node, skill_django, skill_leader])
#     sample_resume.skills.append(DummySkill(skill_name="Other Tech", skill_category_choice='other_category', proficiency_level=3, custom_category_name="Emerging Tech"))
#
#
#     projects_data = [{
#             "project_name": "E-commerce Analytics Dashboard",
#             "description": "A responsive web application that visualizes sales data...",
#             "start_date": date(2022, 3, 1), "end_date": date(2022, 8, 15),
#             "project_url": "https://dashboard-demo.example.com", "repository_url": "https://github.com/example/analytics-dashboard",
#             "bullets": ["Designed and implemented interactive data visualizations..."],
#             "technologies": [skill_react, skill_node]
#         }]
#     for proj_data in projects_data:
#         proj = DummyProject(**{k:v for k,v in proj_data.items() if k not in ["bullets", "technologies"]})
#         for bullet_text in proj_data["bullets"]:
#             proj.bullet_points.append(DummyProjectBulletPoint(bullet_text=bullet_text))
#         if "technologies" in proj_data:
#              proj.technologies_used.extend(proj_data["technologies"])
#         sample_resume.projects.append(proj)
#
#     sample_resume.certifications.extend([
#         DummyCertification(
#             certification_name="AWS Certified Solutions Architect - Professional", issuing_organization="Amazon Web Services",
#             issue_date=date(2022, 4, 10), expiration_date=date(2025, 4, 10),
#             description="Validates expertise in designing distributed systems on AWS.",
#             credential_url="https://aws.amazon.com/certification/...", credential_id="AWS-CSAP-12345", score_percentage=95.0
#         ),
#     ])
#
#     sample_resume.languages.extend([
#         DummyLanguage(language_name="English", proficiency_level="native_fluent"),
#         DummyLanguage(language_name="Spanish", proficiency_level="advanced"),
#     ])
#
#     custom_sections_data = [{
#             "section_title": "Volunteer Experience", "institution_name": "Code for Good", "location": "San Francisco, CA",
#             "start_date": date(2019, 1, 1), "end_date": date(2022, 8, 1),
#             "description": "Volunteered to develop web applications for non-profits.",
#             "section_url": "https://codeforgood.example.org",
#             "bullets": ["Developed a donation tracking system..."]
#         }]
#     for cs_data in custom_sections_data:
#         cs = DummyCustomSection(**{k:v for k,v in cs_data.items() if k != "bullets"})
#         for bullet_text in cs_data.get("bullets", []):
#             cs.bullet_points.append(DummyCustomSectionBulletPoint(bullet_text=bullet_text))
#         sample_resume.custom_sections.append(cs)
#
#     return sample_resume
#
# def create_fresher_resume():
#     """Create a sample resume for a fresh graduate, matching models.py."""
#
#     class DummyQuerySet(list):
#         def exists(self): return len(self) > 0
#         def all(self): return self
#
#     class DummyKeywordTag:
#         def __init__(self, name): self.name = name
#         def __str__(self): return self.name
#
#     class DummyExperienceBulletPoint:
#         def __init__(self, bullet_text):
#             self.bullet_text = bullet_text
#             self.keywords = DummyQuerySet()
#
#     class DummyProjectBulletPoint:
#         def __init__(self, bullet_text):
#             self.bullet_text = bullet_text
#             self.keywords = DummyQuerySet()
#
#     class DummyCustomSectionBulletPoint:
#         def __init__(self, bullet_text):
#             self.bullet_text = bullet_text
#
#     class DummyPersonalInfo:
#         def __init__(self):
#             self.first_name = "Jamie"
#             self.middle_name = ""
#             self.last_name = "Taylor"
#             self.email = "jamie.taylor@example.com"
#             self.phone_number = "(555) 987-6543"
#             self.linkedin_url = "https://linkedin.com/in/jamietaylor"
#             self.github_url = "https://github.com/jamietaylor"
#             self.portfolio_url = "https://jamietaylor.dev"
#             self.address_line1 = "123 University Ave"
#             self.address_line2 = ""
#             self.city = "Boston"
#             self.state = "MA"
#             self.zip_code = "02215"
#             self.country = "USA"
#             self.date_of_birth = date(2001, 3, 15)
#             self.professional_summary = "Recent Computer Science graduate with strong foundations in programming..."
#             self.profile_picture = None
#
#         @property
#         def full_name(self):
#             parts = [self.first_name, self.middle_name, self.last_name]
#             return " ".join(p for p in parts if p)
#
#     class DummyExperience:
#         def __init__(self, job_title, company_name, location, start_date, end_date=None, is_current_job=False, description=""):
#             self.job_title = job_title
#             self.company_name = company_name
#             self.location = location
#             self.start_date = start_date
#             self.end_date = end_date
#             self.is_current_job = is_current_job
#             self.description = description
#             self.bullet_points = DummyQuerySet()
#
#     class DummyEducation:
#         def __init__(self, school_name, degree_name, field_of_study, education_level,
#                      location="", graduation_date=None, description="", gpa=None, start_date=None):
#             self.school_name = school_name
#             self.degree_name = degree_name
#             self.field_of_study = field_of_study
#             self.education_level = education_level
#             self.location = location
#             self.graduation_date = graduation_date
#             self.start_date = start_date
#             self.gpa = gpa
#             self.description = description
#
#     class DummySkill:
#         SKILL_CATEGORY_CHOICES = {
#             'technical': 'Technical', 'soft': 'Soft Skills', 'language': 'Programming Languages',
#             'framework': 'Frameworks/Libraries', 'tool': 'Tools & Technologies', 'database': 'Databases',
#             'cloud': 'Cloud Platforms', 'testing': 'Testing', 'devops': 'DevOps',
#             'design': 'Design', 'project_management': 'Project Management', 'other_category': 'Other'
#         }
#         PROFICIENCY_LEVEL_CHOICES = {
#             1: 'Novice', 2: 'Beginner', 3: 'Skillful', 4: 'Experienced', 5: 'Expert'
#         }
#         def __init__(self, skill_name, skill_category_choice, proficiency_level, custom_category_name=None):
#             self.skill_name = skill_name
#             self.skill_category_choice = skill_category_choice
#             self.proficiency_level = proficiency_level
#             self.custom_category_name = custom_category_name if skill_category_choice == 'other_category' else None
#
#         @property
#         def effective_skill_category(self):
#             if self.skill_category_choice == 'other_category' and self.custom_category_name:
#                 return self.custom_category_name
#             return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice, self.skill_category_choice.replace("_", " ").title())
#
#         def get_skill_category_choice_display(self):
#              return self.SKILL_CATEGORY_CHOICES.get(self.skill_category_choice, self.skill_category_choice.replace("_", " ").title())
#
#         def get_proficiency_level_display(self):
#             return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, "")
#
#     class DummyProject:
#         def __init__(self, project_name, description, start_date=None, end_date=None, project_url=None, repository_url=None):
#             self.project_name = project_name
#             self.description = description
#             self.start_date = start_date
#             self.end_date = end_date
#             self.project_url = project_url
#             self.repository_url = repository_url
#             self.bullet_points = DummyQuerySet()
#             self.technologies_used = DummyQuerySet()
#
#     class DummyCertification:
#         def __init__(self, certification_name, issuing_organization, issue_date=None, expiration_date=None, description=None, credential_url=None, credential_id=None, score_percentage=None):
#             self.certification_name = certification_name
#             self.issuing_organization = issuing_organization
#             self.issue_date = issue_date
#             self.expiration_date = expiration_date
#             self.description = description
#             self.credential_url = credential_url
#             self.credential_id = credential_id
#             self.score_percentage = score_percentage
#
#     class DummyLanguage:
#         PROFICIENCY_LEVEL_CHOICES = {
#             "native_fluent": "Native/Fluent", "advanced": "Advanced",
#             "intermediate": "Intermediate", "basic": "Basic",
#         }
#         def __init__(self, language_name, proficiency_level):
#             self.language_name = language_name
#             self.proficiency_level = proficiency_level
#
#         def get_proficiency_level_display(self):
#             return self.PROFICIENCY_LEVEL_CHOICES.get(self.proficiency_level, self.proficiency_level.title())
#
#     class DummyCustomSection:
#         def __init__(self, section_title, institution_name=None, location=None, start_date=None, end_date=None, description=None, section_url=None):
#             self.section_title = section_title
#             self.institution_name = institution_name
#             self.location = location
#             self.start_date = start_date
#             self.end_date = end_date
#             self.description = description
#             self.section_url = section_url
#             self.bullet_points = DummyQuerySet()
#
#     class DummyResume:
#         def __init__(self):
#             self.id = 2
#             self.title = "Computer Science Graduate Profile"
#             self.personalinfo = DummyPersonalInfo()
#             self.template_name = 'template2'
#             self.slug = "jamie-taylor-computer-science-graduate"
#             self.created_at = datetime.now()
#             self.updated_at = datetime.now()
#             self.user = None
#
#             self.experiences = DummyQuerySet()
#             self.educations = DummyQuerySet()
#             self.skills = DummyQuerySet()
#             self.projects = DummyQuerySet()
#             self.certifications = DummyQuerySet()
#             self.languages = DummyQuerySet()
#             self.custom_sections = DummyQuerySet()
#
#         @property
#         def full_name(self):
#             return self.personalinfo.full_name if self.personalinfo else ""
#
#     fresher_resume = DummyResume()
#
#     fresher_resume.educations.append(
#         DummyEducation(
#             school_name="Boston University", degree_name="Bachelor of Science", field_of_study="Computer Science",
#             education_level="bachelor", location="Boston, MA", graduation_date=date(2023, 5, 15), gpa=3.8,
#             start_date=date(2019, 9, 1), description="Completed final project with honors."
#         )
#     )
#
#     internship = DummyExperience(
#         job_title="Software Development Intern", company_name="TechStart Solutions", location="Boston, MA",
#         start_date=date(2022, 6, 1), end_date=date(2022, 8, 31),
#         description="Assisted in developing and testing new features."
#     )
#     internship.bullet_points.extend([
#         DummyExperienceBulletPoint(bullet_text="Assisted in developing features for an e-commerce platform..."),
#         DummyExperienceBulletPoint(bullet_text="Participated in daily scrum meetings..."),
#     ])
#     fresher_resume.experiences.append(internship)
#
#     # Define some skills for the fresher
#     skill_java_f = DummySkill(skill_name="Java", skill_category_choice='language', proficiency_level=4)
#     skill_python_f = DummySkill(skill_name="Python", skill_category_choice='language', proficiency_level=4)
#     skill_git_f = DummySkill(skill_name="Git", skill_category_choice='tool', proficiency_level=3)
#     skill_problem_solving_f = DummySkill(skill_name="Problem Solving", skill_category_choice='soft', proficiency_level=4)
#
#     fresher_resume.skills.extend([skill_java_f, skill_python_f, skill_git_f, skill_problem_solving_f])
#
#     project1_fresher = DummyProject(
#         project_name="Student Management System",
#         description="A web app for managing student records. Built with Python (Django) and React.",
#         start_date=date(2022, 9, 1), end_date=date(2023, 4, 30),
#         repository_url="https://github.com/jamietaylor/student-ms"
#     )
#     project1_fresher.bullet_points.extend([
#         DummyProjectBulletPoint(bullet_text="Designed database schema with PostgreSQL."),
#         DummyProjectBulletPoint(bullet_text="Developed a responsive front-end."),
#     ])
#     # Assuming skill_react and skill_django_fresher are defined similarly to above
#     # For brevity, let's reuse or assume they are available
#     skill_react_f = DummySkill(skill_name="React", skill_category_choice='framework', proficiency_level=3)
#     skill_django_f = DummySkill(skill_name="Django", skill_category_choice='framework', proficiency_level=3)
#     project1_fresher.technologies_used.extend([skill_react_f, skill_django_f])
#     fresher_resume.projects.append(project1_fresher)
#
#
#     fresher_resume.certifications.append(
#         DummyCertification(
#             certification_name="Oracle Certified Associate, Java SE 8 Programmer", issuing_organization="Oracle",
#             issue_date=date(2022, 11, 10), credential_id="OCAJP-001", score_percentage=85.0
#         )
#     )
#
#     fresher_resume.languages.extend([
#         DummyLanguage(language_name="English", proficiency_level="native_fluent"),
#     ])
#
#     extracurricular = DummyCustomSection(
#         section_title="Extracurricular Activities", institution_name="Boston University Coding Club",
#         location="Boston, MA", start_date=date(2021,9,1), end_date=date(2023,5,1),
#         description="Active member and event organizer."
#     )
#     extracurricular.bullet_points.extend([
#         DummyCustomSectionBulletPoint(bullet_text="Organized weekly coding workshops."),
#         DummyCustomSectionBulletPoint(bullet_text="Participated in National Hackathon 2022."),
#     ])
#     fresher_resume.custom_sections.append(extracurricular)
#
#     return fresher_resume

# def create_experienced_resume():
#     """Create a sample resume for an experienced professional."""
#     from datetime import date
#
#     class DummyQuerySet(list):
#         def exists(self):
#             return len(self) > 0
#
#         def all(self):
#             return self
#
#         def get_skill_type_display(self):
#             return self.skill_type.capitalize() if hasattr(self, 'skill_type') else ""
#
#     class DummyBulletPoint:
#         def __init__(self, description):
#             self.description = description
#             self.keywords = DummyQuerySet()
#
#     class DummyExperience:
#         def __init__(self, job_title, employer, location, start_date, end_date=None, is_current=False):
#             self.job_title = job_title
#             self.employer = employer
#             self.location = location
#             self.start_date = start_date
#             self.end_date = end_date
#             self.is_current = is_current
#             self.bullet_points = DummyQuerySet()
#
#     class DummyEducation:
#         def __init__(self, school_name, location, degree, field_of_study, degree_type, graduation_date, gpa=None,
#                      start_date=None):
#             self.school_name = school_name
#             self.location = location
#             self.degree = degree
#             self.field_of_study = field_of_study
#             self.degree_type = degree_type
#             self.graduation_date = graduation_date
#             self.start_date = start_date
#             self.gpa = gpa
#             self.achievements = "Dean's List: 2015-2017\nSenior Project: Advanced Machine Learning Application\nRecipient of Academic Excellence Scholarship"
#
#     class DummySkill:
#         def __init__(self, name, skill_type, proficiency_level):
#             self.skill_name = name
#             self.skill_type = skill_type
#             self.proficiency_level = proficiency_level
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
#     class DummyProject:
#         def __init__(self, name, summary, start_date, completion_date, project_link=None, github_link=None):
#             self.project_name = name
#             self.summary = summary
#             self.start_date = start_date
#             self.completion_date = completion_date
#             self.project_link = project_link
#             self.github_link = github_link
#             self.bullet_points = DummyQuerySet()
#             self.technologies = DummyQuerySet()
#
#     class DummyCertification:
#         def __init__(self, name, institute, completion_date, expiration_date=None, description=None, link=None,
#                      score=None):
#             self.name = name
#             self.institute = institute
#             self.completion_date = completion_date
#             self.expiration_date = expiration_date
#             self.description = description
#             self.link = link
#             self.score = score
#
#     class DummyLanguage:
#         def __init__(self, name, proficiency):
#             self.language_name = name
#             self.proficiency = proficiency
#
#         def get_proficiency_display(self):
#             return {"basic": "Basic", "intermediate": "Intermediate",
#                     "advanced": "Advanced", "native": "Native"}[self.proficiency]
#
#     class DummyCustomData:
#         def __init__(self, name, completion_date=None, bullet_points=None, description=None, link=None,
#                      institution_name=None):
#             self.name = name
#             self.completion_date = completion_date
#             self.bullet_points = bullet_points
#             self.description = description
#             self.link = link
#             self.institution_name = institution_name
#
#     class DummyResume:
#         def __init__(self):
#             self.id = 1
#             self.first_name = "Alex"
#             self.mid_name = "J."
#             self.last_name = "Morgan"
#             self.full_name = "Alex J. Morgan"
#             self.title = "Senior Full Stack Developer"
#             self.email = "alex.morgan@example.com"
#             self.phone = "(555) 123-4567"
#             self.address = "123 Tech Avenue, Silicon Valley, CA 94123"
#             self.linkedin = "https://linkedin.com/in/alexmorgan"
#             self.github = "https://github.com/alexmorgan"
#             self.portfolio = "https://alexmorgan.dev"
#             self.summary = "Innovative full stack developer with 7+ years of experience building scalable web applications and leading development teams. Specialized in JavaScript, Python, and cloud technologies with a focus on performance optimization and user experience. Passionate about creating elegant solutions to complex problems and implementing best practices in software development."
#
#             # Initialize collections as DummyQuerySet
#             self.experiences = DummyQuerySet()
#             self.educations = DummyQuerySet()
#             self.skills = DummyQuerySet()
#             self.projects = DummyQuerySet()
#             self.certifications = DummyQuerySet()
#             self.languages = DummyQuerySet()
#             self.custom_data = DummyQuerySet()
#
#     # Create a sample resume
#     sample_resume = DummyResume()
#
#     # Add experiences with more variety
#     experiences = [
#         DummyExperience(
#             "Senior Software Engineer",
#             "Tech Innovations Inc.",
#             "San Francisco, CA",
#             date(2020, 6, 1),
#             None,  # end_date
#             True  # is_current
#         ),
#         DummyExperience(
#             "Lead Developer",
#             "Digital Solutions Ltd.",
#             "Seattle, WA",
#             date(2018, 3, 1),
#             date(2020, 5, 31),
#             False
#         ),
#         DummyExperience(
#             "Web Developer",
#             "Creative Web Agency",
#             "Portland, OR",
#             date(2016, 1, 15),
#             date(2018, 2, 28),
#             False
#         ),
#     ]
#
#     # Add bullet points to each experience
#     experiences[0].bullet_points.extend([
#         DummyBulletPoint(
#             "Led a team of 7 developers to deliver a cloud-based enterprise solution that increased customer engagement by 45% and reduced operational costs by 30%"),
#         DummyBulletPoint(
#             "Implemented microservices architecture with Docker and Kubernetes that reduced deployment time by 60% and improved system scalability"),
#         DummyBulletPoint(
#             "Optimized database queries and implemented caching strategies resulting in a 40% improvement in application response time"),
#         DummyBulletPoint(
#             "Mentored junior developers through code reviews and pair programming sessions, improving team productivity by 25%")
#     ])
#
#     experiences[1].bullet_points.extend([
#         DummyBulletPoint(
#             "Designed and developed a customer portal using React and Node.js that increased user satisfaction by 35%"),
#         DummyBulletPoint(
#             "Implemented CI/CD pipelines with Jenkins, reducing integration issues by 50% and deployment failures by 70%"),
#         DummyBulletPoint(
#             "Led the migration from monolithic architecture to microservices, improving system reliability and reducing downtime by 80%")
#     ])
#
#     experiences[2].bullet_points.extend([
#         DummyBulletPoint(
#             "Developed responsive web applications using JavaScript, HTML5, and CSS3 for clients across various industries"),
#         DummyBulletPoint("Integrated third-party APIs to enhance application functionality and user experience"),
#         DummyBulletPoint("Collaborated with UX/UI designers to implement intuitive and accessible user interfaces")
#     ])
#
#     sample_resume.experiences.extend(experiences)
#
#     # Add education with complete details
#     educations = [
#         DummyEducation(
#             "University of Technology",
#             "Boston, MA",
#             "Master of Science",
#             "Computer Science",
#             "master",
#             date(2016, 5, 15),
#             3.92,
#             date(2014, 9, 1)
#         ),
#         DummyEducation(
#             "State University",
#             "Los Angeles, CA",
#             "Bachelor of Science",
#             "Software Engineering",
#             "bachelor",
#             date(2014, 6, 15),
#             3.8,
#             date(2010, 9, 1)
#         )
#     ]
#     sample_resume.educations.extend(educations)
#
#     # Add skills with all skill types
#     skills = [
#         # Technical skills
#         DummySkill("JavaScript", "technical", 95),
#         DummySkill("Python", "language", 90),
#         DummySkill("React", "language", 85),
#         DummySkill("Node.js", "language", 85),
#         DummySkill("TypeScript", "language", 80),
#         DummySkill("Django", "technical", 80),
#         DummySkill("RESTful APIs", "technical", 90),
#         DummySkill("GraphQL", "technical", 75),
#         DummySkill("PostgreSQL", "technical", 85),
#         DummySkill("MongoDB", "technical", 80),
#
#         # Tools
#         DummySkill("AWS", "tool", 85),
#         DummySkill("Docker", "tool", 80),
#         DummySkill("Kubernetes", "tool", 75),
#         DummySkill("Git", "tool", 90),
#         DummySkill("Jenkins", "tool", 80),
#         DummySkill("JIRA", "tool", 85),
#
#         # Soft skills
#         DummySkill("Team Leadership", "soft", 90),
#         DummySkill("Project Management", "soft", 85),
#         DummySkill("Communication", "soft", 95),
#         DummySkill("Problem Solving", "soft", 90),
#         DummySkill("Agile Methodologies", "soft", 85)
#     ]
#     sample_resume.skills.extend(skills)
#
#     # Add projects with technologies
#     projects = [
#         DummyProject(
#             "E-commerce Analytics Dashboard",
#             "A responsive web application that visualizes sales data and customer insights for online retailers",
#             date(2022, 3, 1),
#             date(2022, 8, 15),
#             "https://dashboard-demo.example.com",
#             "https://github.com/example/analytics-dashboard"
#         ),
#         DummyProject(
#             "Content Management System",
#             "A customizable CMS with advanced user permissions and real-time collaboration features",
#             date(2021, 5, 1),
#             date(2021, 12, 10),
#             "https://cms-example.com",
#             "https://github.com/example/modern-cms"
#         )
#     ]
#
#     # Add bullet points to projects
#     projects[0].bullet_points.extend([
#         DummyBulletPoint(
#             "Designed and implemented interactive data visualizations using D3.js and React, providing actionable insights on sales trends"),
#         DummyBulletPoint(
#             "Integrated with RESTful APIs to fetch real-time sales and inventory data from multiple sources"),
#         DummyBulletPoint("Implemented user authentication and role-based access control to ensure data security"),
#         DummyBulletPoint("Created a responsive design that works seamlessly across desktop and mobile devices")
#     ])
#
#     projects[1].bullet_points.extend([
#         DummyBulletPoint("Developed a plugin-based architecture allowing for easy extension of core functionality"),
#         DummyBulletPoint("Implemented real-time collaboration features using WebSockets and Redis"),
#         DummyBulletPoint("Created a customizable workflow engine to support complex content approval processes"),
#         DummyBulletPoint("Optimized performance using lazy loading and efficient caching strategies")
#     ])
#
#     # Add technologies to projects
#     tech_map = {
#         "React": "technical",
#         "Node.js": "technical",
#         "MongoDB": "technical",
#         "Express.js": "technical",
#         "D3.js": "technical",
#         "Redis": "technical",
#         "AWS S3": "tool",
#         "Docker": "tool"
#     }
#
#     for tech_name, tech_type in list(tech_map.items())[:4]:  # First 4 for project 1
#         projects[0].technologies.append(DummySkill(tech_name, tech_type, 85))
#
#     for tech_name, tech_type in list(tech_map.items())[4:]:  # Last 4 for project 2
#         projects[1].technologies.append(DummySkill(tech_name, tech_type, 85))
#
#     sample_resume.projects.extend(projects)
#
#     # Add certifications with all fields
#     certifications = [
#         DummyCertification(
#             "AWS Certified Solutions Architect - Professional",
#             "Amazon Web Services",
#             date(2022, 4, 10),
#             date(2025, 4, 10),
#             "Professional certification validating expertise in designing distributed systems on AWS",
#             "https://aws.amazon.com/certification/certified-solutions-architect-professional/",
#             "950/1000"
#         ),
#         DummyCertification(
#             "Certified Kubernetes Administrator",
#             "Cloud Native Computing Foundation",
#             date(2021, 8, 15),
#             date(2024, 8, 15),
#             "Certification for Kubernetes administration and deployment expertise",
#             "https://www.cncf.io/certification/cka/",
#             "92%"
#         )
#     ]
#     sample_resume.certifications.extend(certifications)
#
#     # Add languages
#     languages = [
#         DummyLanguage("English", "native"),
#         DummyLanguage("Spanish", "advanced"),
#         DummyLanguage("French", "intermediate"),
#         DummyLanguage("Mandarin", "basic")
#     ]
#     sample_resume.languages.extend(languages)
#
#     # Add custom data sections
#     custom_data_sections = [
#         DummyCustomData(
#             "Volunteer Experience",
#             date(2022, 8, 1),
#             "Developed a donation tracking system for a local food bank\nCreated a volunteer management application for disaster relief coordination\nMentored high school students in programming basics through weekly workshops",
#             "Volunteered with Code for Good to develop web applications for non-profit organizations",
#             "https://codeforgood.example.org",
#             "Code for Good"
#         ),
#         DummyCustomData(
#             "Publications",
#             date(2021, 3, 15),
#             "Published 'Scalable Architecture Patterns for Modern Web Applications' in Journal of Software Engineering\nContributed to 'Best Practices in Microservices Design' technical white paper\nAuthored multiple technical blog posts on Medium's Better Programming publication",
#             "Technical publications related to software architecture and development",
#             "https://medium.com/@alexmorgan",
#             "Various Publishers"
#         ),
#         DummyCustomData(
#             "Awards & Recognition",
#             date(2021, 11, 10),
#             "Developer of the Year, Company Awards 2021\nHackathon Winner, Healthcare Innovation Challenge 2020\nRecognized for Outstanding Technical Leadership, Q3 2019",
#             "Professional recognition and awards received throughout career"
#         )
#     ]
#     sample_resume.custom_data.extend(custom_data_sections)
#
#     # Modify DummyQuerySet to support template regroup tag
#     sample_resume.skills.get_skill_type_display = lambda: 'Technical'
#
#     return sample_resume
#
#
# def create_fresher_resume():
#     """Create a sample resume for a fresh graduate with appropriate data."""
#     from datetime import date
#
#     class DummyQuerySet(list):
#         def exists(self):
#             return len(self) > 0
#
#         def all(self):
#             return self
#
#         def get_skill_type_display(self):
#             return self.skill_type.capitalize() if hasattr(self, 'skill_type') else ""
#
#     class DummyBulletPoint:
#         def __init__(self, description):
#             self.description = description
#             self.keywords = DummyQuerySet()
#
#     class DummyExperience:
#         def __init__(self, job_title, employer, location, start_date, end_date=None, is_current=False):
#             self.job_title = job_title
#             self.employer = employer
#             self.location = location
#             self.start_date = start_date
#             self.end_date = end_date
#             self.is_current = is_current
#             self.bullet_points = DummyQuerySet()
#
#     class DummyEducation:
#         def __init__(self, school_name, location, degree, field_of_study, degree_type, graduation_date, gpa=None,
#                      start_date=None):
#             self.school_name = school_name
#             self.location = location
#             self.degree = degree
#             self.field_of_study = field_of_study
#             self.degree_type = degree_type
#             self.graduation_date = graduation_date
#             self.start_date = start_date
#             self.gpa = gpa
#             self.achievements = "Dean's List: 2022-2023\nCompleted final project with highest honors\nSelected for prestigious internship program\nWon 2nd place in university hackathon"
#
#     class DummySkill:
#         def __init__(self, name, skill_type, proficiency_level):
#             self.skill_name = name
#             self.skill_type = skill_type
#             self.proficiency_level = proficiency_level
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
#     class DummyProject:
#         def __init__(self, name, summary, start_date, completion_date, project_link=None, github_link=None):
#             self.project_name = name
#             self.summary = summary
#             self.start_date = start_date
#             self.completion_date = completion_date
#             self.project_link = project_link
#             self.github_link = github_link
#             self.bullet_points = DummyQuerySet()
#             self.technologies = DummyQuerySet()
#
#     class DummyCertification:
#         def __init__(self, name, institute, completion_date, expiration_date=None, description=None, link=None,
#                      score=None):
#             self.name = name
#             self.institute = institute
#             self.completion_date = completion_date
#             self.expiration_date = expiration_date
#             self.description = description
#             self.link = link
#             self.score = score
#
#     class DummyLanguage:
#         def __init__(self, name, proficiency):
#             self.language_name = name
#             self.proficiency = proficiency
#
#         def get_proficiency_display(self):
#             return {"basic": "Basic", "intermediate": "Intermediate",
#                     "advanced": "Advanced", "native": "Native"}[self.proficiency]
#
#     class DummyCustomData:
#         def __init__(self, name, completion_date=None, bullet_points=None, description=None, link=None,
#                      institution_name=None):
#             self.name = name
#             self.completion_date = completion_date
#             self.bullet_points = bullet_points
#             self.description = description
#             self.link = link
#             self.institution_name = institution_name
#
#     class DummyResume:
#         def __init__(self):
#             self.id = 1
#             self.first_name = "Jamie"
#             self.mid_name = ""
#             self.last_name = "Taylor"
#             self.full_name = "Jamie Taylor"
#             self.title = "Computer Science Graduate"
#             self.email = "jamie.taylor@example.com"
#             self.phone = "(555) 987-6543"
#             self.address = "123 University Ave, Boston, MA 02215"
#             self.linkedin = "https://linkedin.com/in/jamietaylor"
#             self.github = "https://github.com/jamietaylor"
#             self.portfolio = "https://jamietaylor.dev"
#             self.summary = "Recent Computer Science graduate with strong foundations in programming, algorithms, and web development. Completed multiple projects showcasing skills in Python, Java, and JavaScript. Eager to apply academic knowledge and technical abilities in a professional software development role to build innovative and efficient solutions."
#
#             # Initialize collections
#             self.experiences = DummyQuerySet()
#             self.educations = DummyQuerySet()
#             self.skills = DummyQuerySet()
#             self.projects = DummyQuerySet()
#             self.certifications = DummyQuerySet()
#             self.languages = DummyQuerySet()
#             self.custom_data = DummyQuerySet()
#
#     # Create fresh graduate resume
#     fresher_resume = DummyResume()
#
#     # Add education (primary focus for a fresher resume)
#     education = DummyEducation(
#         "Boston University",
#         "Boston, MA",
#         "Bachelor of Science",
#         "Computer Science",
#         "bachelor",
#         date(2023, 5, 15),  # Recent graduation
#         3.8,
#         date(2019, 9, 1)
#     )
#     fresher_resume.educations.append(education)
#
#     # Add internship experience (limited experience for a fresher)
#     internship = DummyExperience(
#         "Software Development Intern",
#         "TechStart Solutions",
#         "Boston, MA",
#         date(2022, 6, 1),
#         date(2022, 8, 31),
#         False
#     )
#     internship.bullet_points.extend([
#         DummyBulletPoint(
#             "Assisted in developing and testing features for the company's e-commerce platform using React and Node.js"),
#         DummyBulletPoint(
#             "Participated in daily scrum meetings and collaborated with senior developers on code reviews"),
#         DummyBulletPoint("Implemented responsive design improvements that enhanced mobile user experience by 25%")
#     ])
#     fresher_resume.experiences.append(internship)
#
#     # Add part-time job during studies
#     part_time = DummyExperience(
#         "Computer Lab Assistant",
#         "Boston University IT Department",
#         "Boston, MA",
#         date(2021, 9, 1),
#         date(2023, 5, 15),
#         False
#     )
#     part_time.bullet_points.extend([
#         DummyBulletPoint("Provided technical support to students and faculty for hardware and software issues"),
#         DummyBulletPoint("Maintained computer lab equipment and assisted in software installations and updates"),
#         DummyBulletPoint("Conducted basic programming tutoring sessions for introductory CS courses")
#     ])
#     fresher_resume.experiences.append(part_time)
#
#     # Add projects (important for freshers to showcase skills)
#     project1 = DummyProject(
#         "Student Management System",
#         "A full-stack web application for managing student records, courses, and grades",
#         date(2022, 9, 1),
#         date(2023, 4, 30),
#         "https://student-ms-demo.example.com",
#         "https://github.com/jamietaylor/student-ms"
#     )
#     project1.bullet_points.extend([
#         DummyBulletPoint(
#             "Designed and implemented a database schema with MySQL to store student and course information"),
#         DummyBulletPoint(
#             "Developed a responsive front-end using React and Bootstrap that allows for intuitive navigation"),
#         DummyBulletPoint(
#             "Implemented secure user authentication with different permission levels for students and administrators")
#     ])
#     project1.technologies.extend([
#         DummySkill("React", "technical", 80),
#         DummySkill("Node.js", "technical", 75),
#         DummySkill("MySQL", "technical", 85),
#         DummySkill("Bootstrap", "technical", 90)
#     ])
#
#     project2 = DummyProject(
#         "Weather Forecast Mobile App",
#         "A cross-platform mobile application showing detailed weather forecasts and alerts",
#         date(2021, 11, 1),
#         date(2022, 2, 28),
#         "https://weather-app-demo.example.com",
#         "https://github.com/jamietaylor/weather-app"
#     )
#     project2.bullet_points.extend([
#         DummyBulletPoint("Created a cross-platform mobile app using Flutter that fetches and displays weather data"),
#         DummyBulletPoint("Integrated with OpenWeatherMap API to retrieve real-time weather information"),
#         DummyBulletPoint("Implemented location-based services to automatically detect the user's current location")
#     ])
#     project2.technologies.extend([
#         DummySkill("Flutter", "technical", 75),
#         DummySkill("Dart", "language", 70),
#         DummySkill("REST APIs", "technical", 80),
#         DummySkill("Firebase", "tool", 65)
#     ])
#
#
#
#     fresher_resume.projects.extend([project1, project2])
#
#     # Add skills (focus on skills relevant for entry-level positions)
#     skills = [
#         # Programming languages
#         DummySkill("Java", "language", 85),
#         DummySkill("Python", "language", 90),
#         DummySkill("JavaScript", "language", 80),
#         DummySkill("HTML/CSS", "language", 85),
#         DummySkill("SQL", "language", 75),
#         DummySkill("C++", "language", 70),
#
#         # Technical skills
#         DummySkill("Data Structures", "technical", 85),
#         DummySkill("Algorithms", "technical", 80),
#         DummySkill("Object-Oriented Programming", "technical", 85),
#         DummySkill("Web Development", "technical", 80),
#         DummySkill("Mobile Development", "technical", 75),
#         DummySkill("Database Design", "technical", 70),
#
#         # Tools and frameworks
#         DummySkill("Git", "tool", 85),
#         DummySkill("React", "tool", 75),
#         DummySkill("Node.js", "tool", 70),
#         DummySkill("Flutter", "tool", 65),
#         DummySkill("Docker", "tool", 60),
#         DummySkill("VS Code", "tool", 90),
#
#         # Soft skills
#         DummySkill("Problem Solving", "soft", 85),
#         DummySkill("Teamwork", "soft", 90),
#         DummySkill("Communication", "soft", 85),
#         DummySkill("Time Management", "soft", 80),
#         DummySkill("Adaptability", "soft", 85)
#     ]
#     fresher_resume.skills.extend(skills)
#
#     # Add certifications (entry-level certifications)
#     certifications = [
#         DummyCertification(
#             "AWS Certified Cloud Practitioner",
#             "Amazon Web Services",
#             date(2023, 1, 15),
#             date(2026, 1, 15),
#             "Foundational certification validating understanding of AWS Cloud",
#             "https://aws.amazon.com/certification/certified-cloud-practitioner/",
#             "820/1000"
#         ),
#         DummyCertification(
#             "Oracle Certified Associate Java Programmer",
#             "Oracle",
#             date(2022, 6, 10),
#             None,
#             "Entry-level certification for Java programming language",
#             "https://education.oracle.com/java-certification-path",
#             "85%"
#         ),
#         DummyCertification(
#             "Microsoft Certified: Azure Fundamentals",
#             "Microsoft",
#             date(2022, 11, 20),
#             None,
#             "Basic understanding of cloud services and Microsoft Azure",
#             "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/",
#             "875/1000"
#         )
#     ]
#     fresher_resume.certifications.extend(certifications)
#
#     # Add languages
#     languages = [
#         DummyLanguage("English", "native"),
#         DummyLanguage("Spanish", "intermediate"),
#         DummyLanguage("French", "basic")
#     ]
#     fresher_resume.languages.extend(languages)
#
#     # Add extracurricular activities and achievements (important for freshers)
#     custom_data_sections = [
#         DummyCustomData(
#             "Extracurricular Activities",
#             date(2023, 5, 1),
#             "Member of the University Coding Club (2021-2023)\nParticipated in three Hackathons, winning 2nd place in CodeJam 2022\nVolunteered as a peer mentor for first-year Computer Science students\nContributed to open-source projects on GitHub",
#             "Active participation in university and community technical activities",
#             None,
#             "Boston University"
#         ),
#
#     ]
#     fresher_resume.custom_data.extend(custom_data_sections)
#
#     # Modify DummyQuerySet to support template regroup tag
#     fresher_resume.skills.get_skill_type_display = lambda: 'Technical'
#
#     return fresher_resume

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
