from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc

import json

register = template.Library()

@register.filter
def split(str,splitter):
    return str.split(splitter)

@register.filter
def to_json(query_obj):
    return mark_safe(json.dumps(query_obj))

@register.filter
def short_label(query_obj):
    # Collect the output
    output = []
    icon = '<i class="icon-{}"></i>'
    # Split the query into each journal
    for query in query_obj['queries']:
        text = query.get('text','')
        line_bits = [icon.format(esc(query.get('type', '')))]
        # Check if the journal name is longer than we want
        if len(text) <= 15:
            line_bits.append(esc(text))
        else:
            line_bits.extend([
                '<span title="',
                esc(text),
                '">',
                esc(text[0:13]),
                '&hellip;</span>'])
        output.append(''.join(line_bits))
    return mark_safe('<br />'.join(output))

@register.filter
def query_count(count):
    """
    Prefix single digits with a 0
    """
    return "{0:0=2d}".format(count)
