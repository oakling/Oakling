import urllib
import urllib2
from BeautifulSoup import BeautifulStoneSoup

from utils import change_keys

def search(search_term, start=1, max_results=10):
    url = "http://adsabs.harvard.edu/cgi-bin/basic_connect?"
    query_args = {'qsearch': search_term,
                  'start_nr':start,
                  'nr_to_return':max_results,
                  'data_type':'SHORT_XML',
                  'version':1}

    encoded_args = urllib.urlencode(query_args)
    headers = { 'User-Agent' : 'Mozilla/5.0', }
    req = urllib2.Request(url + encoded_args, headers=headers)

    atom_results = BeautifulStoneSoup(urllib2.urlopen(req))

    return [_format(result) for result in atom_results('record')]

def _format(entry):
    result={}
    result['title']=entry.find('title').text
    result['authors'] = [author.text for author in entry('author')]
    if entry.find('doi'):
        result['doi'] = entry.find('doi').text
    return result
