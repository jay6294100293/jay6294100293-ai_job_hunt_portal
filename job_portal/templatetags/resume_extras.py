from django import template
import re
from decimal import Decimal

register = template.Library()

from django import template

# job_portal/templatetags/resume_extras.py
from django import template
from job_portal.models import Resume  # Import Resume model

@register.filter
def get_item(dictionary, key):
    """
    Allows accessing dictionary items with a variable key in Django templates.
    Usage: {{ my_dictionary|get_item:my_key_variable }}
    """
    return dictionary.get(key)


@register.simple_tag
def step_status(resume, step_key, current_step_key, wizard_steps_config=None):
    """
    Determines the CSS class for a wizard step based on its completion status.
    Args:
        resume (Resume): The current Resume object.
        step_key (str): The key of the step being evaluated (e.g., 'personal_info').
        current_step_key (str): The key of the currently active step in the wizard.
        wizard_steps_config (dict): The WIZARD_STEPS configuration from the view,
                                    containing model and form info if needed for complex checks.
    Returns:
        str: CSS class ('active', 'completed', or 'default').
    """
    if step_key == current_step_key:
        return 'active'

    completed = False
    if resume and resume.pk:  # Ensure resume object is not None and has been saved
        try:
            if step_key == 'personal_info':
                # Check for essential personal info fields directly on the Resume model
                # For example, if first_name and email are considered essential for completion.
                # You can adjust this logic based on what you deem "complete" for this step.
                completed = bool(resume.first_name and resume.email and resume.phone)
            elif step_key == 'summary':
                # Check for the summary field directly on the Resume model
                completed = bool(resume.summary and resume.summary.strip())
            elif step_key == 'experience':
                completed = resume.experiences.exists()  # related_name='experiences'
            elif step_key == 'education':
                completed = resume.educations.exists()  # related_name='educations'
            elif step_key == 'skills':
                completed = resume.skills.exists()  # related_name='skills'
            elif step_key == 'projects':
                completed = resume.projects.exists()  # related_name='projects'
            elif step_key == 'certifications':
                completed = resume.certifications.exists()  # related_name='certifications'
            elif step_key == 'languages':
                completed = resume.languages.exists()  # related_name='languages'
            elif step_key == 'custom_sections':  # Key used in WIZARD_STEPS
                # CustomData model has related_name='custom_sections'
                completed = resume.custom_sections.exists()
            # Add more steps here if your WIZARD_STEPS dict in views.py has other keys

        except AttributeError:
            # This can happen if a related object accessor doesn't exist yet
            completed = False
        except Exception:
            # Catch any other potential errors during attribute checking
            completed = False  # Default to not completed on error

    return 'completed' if completed else 'default'


@register.filter(name='get_form_field_value')
def get_form_field_value(form, field_name):
    """
    Retrieves the value of a form field.
    Useful for pre-filling fields or debugging.
    """
    field = form.fields.get(field_name)
    if field:
        return form[field_name].value()
    return None


@register.filter(name='get_formset_field_value')
def get_formset_field_value(form, field_name):
    """
    Retrieves the value of a field within a formset's form.
    """
    if hasattr(form, 'initial') and field_name in form.initial:
        return form.initial[field_name]
    if hasattr(form, 'cleaned_data') and field_name in form.cleaned_data:
        return form.cleaned_data[field_name]
    bound_field = form[field_name]
    if bound_field:
        return bound_field.value()
    return ''

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
# Numeric operations
@register.filter(name='mul')
def multiply(value, arg):
    """
    Multiply the value by the argument.
    Usage: {{ value|mul:10 }}
    """
    try:
        # Convert both to float to handle various numeric types
        return float(value) * float(arg)
    except (ValueError, TypeError):
        # Return empty string or original value on error
        return value


@register.filter(name='div')
def divide(value, arg):
    """
    Divide the value by the argument.
    Usage: {{ value|div:10 }}
    """
    try:
        # Convert both to float to handle various numeric types
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        # Return empty string or original value on error
        return value


# String operations
@register.filter
def trim(value):
    """Trim whitespace from the beginning and end of a string."""
    if value is None:
        return ''
    return str(value).strip()


@register.filter
def split(value, arg):
    """Split a string by the given argument and return a list."""
    if value is None:
        return []
    return value.split(arg)


# Range operations
@register.filter
def get_range(value):
    """Return a range from 1 to value"""
    try:
        value = int(value)
        return range(1, value + 1)
    except (ValueError, TypeError):
        return range(0)


@register.filter(name='add_class')
def add_class(value, arg):
    """
    Add a CSS class to an HTML element's existing class attribute.
    Works with both form fields and HTML strings.
    """
    if value is None:
        return ''

    # Check if it's a form field
    if hasattr(value, 'field') and hasattr(value.field, 'widget'):
        css_classes = value.field.widget.attrs.get('class', '')

        # If there are already classes, add a space before adding the new class
        if css_classes:
            css_classes = f"{css_classes} {arg}"
        else:
            css_classes = arg

        # Set the updated classes back to the widget
        value.field.widget.attrs['class'] = css_classes

        return value

    # If it's a string (SafeString or regular string), assume it's HTML
    elif isinstance(value, str):
        # Check for class attribute
        if 'class="' in value:
            return value.replace('class="', f'class="{arg} ')
        elif "class='" in value:
            return value.replace("class='", f"class='{arg} ")
        else:
            # If no class exists, add it right after the first tag opening
            tag_end = value.find('>')
            if tag_end != -1:
                return value[:tag_end] + f' class="{arg}"' + value[tag_end:]

    # Return the value unchanged if it's neither a form field nor a string
    return value

@register.filter
def split(value, arg):
    """
    Splits a string by the specified delimiter and returns a list.
    Usage: {{ value|split:"," }}
    """
    if value:
        return value.split(arg)
    return []

@register.filter(name='attr')
def set_attribute(field, attr_name_value):
    """
    Set an HTML attribute (name and value) for a form field's widget.
    Usage: {{ form.field|attr:"name:value" }}
    """
    if field is None:
        return ''

    # Split the attribute name and value at the first colon
    parts = attr_name_value.split(':', 1)
    if len(parts) != 2:
        return field  # Return unchanged if format is incorrect

    attr_name, attr_value = parts
    attr_name = attr_name.strip()
    attr_value = attr_value.strip()

    # Set the attribute
    if hasattr(field, 'field') and hasattr(field.field, 'widget'):
        field.field.widget.attrs[attr_name] = attr_value

    return field


# HTML string operations
@register.filter(name='html_add_class')
def html_add_class(value, arg):
    """
    Add a CSS class to an HTML string that might already have a class attribute.
    Usage: {{ '<div class="old-class">Content</div>'|html_add_class:"new-class" }}
    """
    if value is None:
        return ''

    if 'class="' in value:
        return value.replace('class="', f'class="{arg} ')
    elif "class='" in value:
        return value.replace("class='", f"class='{arg} ")
    else:
        # If no class exists, add it right after the first tag opening
        tag_end = value.find('>')
        if tag_end != -1:
            return value[:tag_end] + f' class="{arg}"' + value[tag_end:]
    return value


@register.filter(name='html_attr')
def set_html_attribute(value, attr_name_value):
    """
    Set an HTML attribute in an HTML string.
    Usage: {{ '<div>Content</div>'|html_attr:"data-id:123" }}
    """
    if value is None:
        return ''

    parts = attr_name_value.split(':', 1)
    if len(parts) != 2:
        return value  # Return unchanged if format is incorrect

    attr_name, attr_value = parts
    attr_name = attr_name.strip()
    attr_value = attr_value.strip()

    # Check if attribute already exists
    pattern = f'{attr_name}=["\'](.*?)["\']'
    if re.search(pattern, value):
        # Replace existing attribute
        return re.sub(pattern, f'{attr_name}="{attr_value}"', value)
    else:
        # Add new attribute
        tag_end = value.find('>')
        if tag_end != -1:
            return value[:tag_end] + f' {attr_name}="{attr_value}"' + value[tag_end:]

    return value