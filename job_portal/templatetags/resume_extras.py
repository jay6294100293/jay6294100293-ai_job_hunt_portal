from django import template
import re
from decimal import Decimal

register = template.Library()

from django import template


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