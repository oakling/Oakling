import sys
import urllib2
import feedparser
import time
import re

from classification import classify

SCRAPER_DOMAINS = ['www.arxiv.org',]

def arxiv_id(url):
    return remove_vNumber(re.search('(?:abs|pdf)/(.*)', url).groups()[0])

def remove_vNumber(s):
    return re.sub(r'v[0-9]+', '', s)
    

def arxiv_api(ids):
    """Return a list of arxiv papers."""

    base_url = 'http://export.arxiv.org/api/query?id_list='

    response = urllib2.urlopen(base_url + ','.join(ids)).read()
    results = feedparser.parse(response)['items']
    papers = []

    for result in results:
        paper = {}
        paper['title'] = result.title
        paper['author_names'] = [author.name for author in result.authors]
        paper['abstract'] = result.summary
        paper['categories'] = {'arxiv':None}
        paper['date_revised'] = time.mktime(result.updated_parsed)
        paper['date_published'] = time.mktime(result.published_parsed)

        paper['ids'] = {'arxiv': arxiv_id(result.link)}
        if 'arxiv_doi' in result:
            paper['ids']['doi'] = result.arxiv_doi

        paper['source_urls'] = [remove_vNumber(result.link)]

        paper['categories'] = classify([tag['term'] for tag in result.tags])
        paper['journal'] = 'arxiv:' + result.arxiv_primary_category['term']
        paper['citation'] = {'journal':paper['journal'],
                             'year':result.published_parsed.tm_year}
        papers.append(paper)
    return papers


def scrape(url):

    paper_id = arxiv_id(url)
    return arxiv_api([paper_id])[0]

if __name__ == '__main__':
  print scrape(sys.argv[1]) 
