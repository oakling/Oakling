from django.template import Library
from django.utils.safestring import mark_safe
import urlparse

register = Library()

@register.filter
def domain(value):
  url_parsed = urlparse.urlparse(value)
  return mark_safe(url_parsed.netloc)

@register.filter
def scraped_location(doc):
  if 'source_url' in doc:
    return doc['source_url']
  elif 'source_urls' in doc:
    return doc['source_urls'][len(doc['source_urls'])-1]
  else:
    return None
