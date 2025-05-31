from django.shortcuts import render
from django.http import Http404
from django.utils.translation import gettext_lazy as _

# Assuming your demo data functions are in resume_support_code.py
# Adjust the import path if your file is located elsewhere or named differently.
from services.supporting_codes.resume_support_code import create_experienced_resume, create_fresher_resume

# Define the available demo templates and their actual file paths
# The keys (e.g., 'template1') will be used in the URL
AVAILABLE_DEMO_TEMPLATES = {
    'template1': 'resumes/templates/template1.html',
    'template2': 'resumes/templates/template2.html',
    'template3': 'resumes/templates/template3.html',
    'template4': 'resumes/templates/template4.html',
    'template5': 'resumes/templates/template5.html',
    'template6': 'resumes/templates/template6.html',
}

# Define available demo resume types
AVAILABLE_DEMO_TYPES = {
    'experienced': create_experienced_resume,
    'fresher': create_fresher_resume,
}


def preview_demo_resume(request, resume_type_slug, template_slug):
    """
    Renders a specific resume template with a chosen type of demo data.
    """
    if resume_type_slug not in AVAILABLE_DEMO_TYPES:
        raise Http404(
            _(f"Demo resume type '{resume_type_slug}' not found. Available types are: {', '.join(AVAILABLE_DEMO_TYPES.keys())}"))

    if template_slug not in AVAILABLE_DEMO_TEMPLATES:
        raise Http404(
            _(f"Demo template '{template_slug}' not found. Available templates are: {', '.join(AVAILABLE_DEMO_TEMPLATES.keys())}"))

    # Get the function to create the demo resume data
    create_demo_resume_func = AVAILABLE_DEMO_TYPES[resume_type_slug]
    resume_data = create_demo_resume_func()

    # Get the template file path
    template_path = AVAILABLE_DEMO_TEMPLATES[template_slug]

    # It's useful for the template to know it's a demo, and which one
    # The demo resume objects (DummyResume) already have a 'title' and 'template_name' attribute
    # but we are overriding the template_name via URL here for preview.
    # We can also set a specific title for the demo page.

    page_title = _(f"Demo Preview: {resume_type_slug.capitalize()} Resume - {template_slug.capitalize()}")

    # The demo resume object itself is passed as 'resume'
    # The actual resume templates expect the main data object to be named 'resume'
    context = {
        'resume': resume_data,
        'page_title': page_title,
        'is_demo_preview': True,  # You can use this in templates if needed
        'current_demo_template': template_slug,
        'current_resume_type': resume_type_slug,
        # Provide a list of all templates and types for potential navigation in the demo view itself (optional)
        'all_template_slugs': AVAILABLE_DEMO_TEMPLATES.keys(),
        'all_resume_types': AVAILABLE_DEMO_TYPES.keys(),
    }

    return render(request, template_path, context)