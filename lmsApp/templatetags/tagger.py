from django import template
import json
register = template.Library()

@register.simple_tag
def underscoreTag(obj, attribute):
    # Ensure obj is a dictionary or an object with attributes
    if isinstance(obj, dict) and attribute in obj:
        return obj.get(attribute, None)
    elif hasattr(obj, attribute):
        return getattr(obj, attribute, None)
    return ''



@register.simple_tag
def underscoreBookTag(obj, attribute):
    if obj and obj[attribute]:
        return obj[attribute]
    if obj.get(attribute) is not None:
        return obj[attribute]
    # Handle other cases if needed
    return {}  # Or raise an exception