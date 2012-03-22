import urllib
import urllib2
try: import simplejson as json
except ImportError: import json

from utils import change_keys

def search(search_term, page_num=1, per_page=10):
    url = "http://www.citeulike.org/json/search/all?"
    data = {'title':'title',
            'journal':'journal',
            'authors':'authors',
            'doi':'doi',
            'uri':'href'}
    query_args = {'q': search_term, 'page':page_num, 'per_page':per_page}

    encoded_args = urllib.urlencode(query_args)
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request(url + encoded_args, headers=headers)

    json_results = urllib2.urlopen(req)
    results = json.load(json_results)

    return [change_keys(data, result) for result in results]
