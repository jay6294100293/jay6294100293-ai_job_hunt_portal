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
