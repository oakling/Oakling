import urllib
import urllib2
import feedparser

from utils import change_keys

def search(search_term, start=1, max_results=50):
    url = "http://export.arxiv.org/api/query?"
    query_args = {'search_query': search_term, 'start':start,
                  'max_results':max_results}

    encoded_args = urllib.urlencode(query_args)
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request(url + encoded_args, headers=headers)

    atom_results = feedparser.parse(urllib2.urlopen(req))
    results = atom_results.entries

    return [_format(result) for result in results]

def _format(entry):
    data = {'title':'title',
            'journal':'arxiv_journal_ref',
            'authors':'authors',
            'doi':'arxiv_doi',
            'uri':'id'}
    result = change_keys(data, entry)
    result['authors'] = [author['name'] for author in result['authors']]
    return result
