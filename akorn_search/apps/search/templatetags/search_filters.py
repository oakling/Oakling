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
    # Split the query into each journal
    for query in query_obj['queries'].itervalues():
        b = query.get('label','')
        # Check if the journal name is longer than we want
        if len(b) <= 22:
                output.append(esc(b))
        else:
            output.append(''.join(['<span title="',esc(b),'">',
                esc(b[0:20]),'&hellip;</span>']))
    return mark_safe(' +<br />'.join(output))
