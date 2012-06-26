from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc

register = template.Library()

@register.filter
def split(str,splitter):
    return str.split(splitter)

@register.filter
def short_query(str):
    # Collect the output
    output = []
    # Split the query into each journal
    for b in str.split('+'):
        # Check if the journal name is longer than we want
        if len(b) <= 42:
                output.append(esc(b))
        else:
            output.append(''.join(['<span title="',esc(b),'">',
                esc(b[0:40]),'&hellip;</span>']))
    return mark_safe(' +<br />'.join(output))
