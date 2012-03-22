import urllib
import urllib2
try: import simplejson as json
except ImportError: import json

from utils import change_keys

from django.conf import settings

def search(search_term, page_num=1, per_page=10):
    url = "http://api.mendeley.com/oapi/documents/search/"
    data = {'title':'title',
            'journal':'publication_outlet',
            'authors':'authors',
            'doi':'doi',
            'uri':'mendeley_url'}
    query_args = {'page':page_num,
                  'items':per_page,
                  'consumer_key':settings.MENDELEY_CONSUMER_KEY}

    encoded_args = urllib.urlencode(query_args)
    url = url + urllib2.quote(search_term) + '?'
    headers = { 'User-Agent' : 'Mozilla/5.0' }

    req = urllib2.Request(url + encoded_args, headers=headers)

    try:
      json_results = urllib2.urlopen(req)
    except urllib2.HTTPError:
      return []

    results = json.load(json_results)

    results = results['documents']

    return [change_keys(data, result) for result in results]
