from django.template import Library
from django.utils.safestring import mark_safe

str = unicode

register = Library()

@register.filter
def to_dl(input_dict, safe=True):
    output = ['<dl>']
    if not input_dict:
        return ''
    for key, value in input_dict.items():
        if not value:
            continue
        output.extend(['<dt>', key, '<dt>'])
        output.append('<dd>')
        val_type = type(value)
        if val_type == dict:
            output.append(to_dl(value, safe=False))
        elif val_type == list:
            output.append('<ul>')
            output.extend([''.join(['<li>',str(_),'</li>']) for _ in value])
            output.append('</ul>')
        else:
            output.append(str(value))
        output.append('</dd>')
    output.append('</dl>')
    output = ''.join(output)
    if safe:
        return mark_safe(output)
    else:
        return output
