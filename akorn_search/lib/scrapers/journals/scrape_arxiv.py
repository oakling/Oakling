import urllib2
import re
import urlparse
import sys

from lib.scrapers.journals.utils import get_response_chain

#SCRAPER_DOMAINS = ['www.arxiv.org','arxiv.org']

def resolve_doi(doi):
  try:
    page = urllib2.urlopen("http://dx.doi.org/%s" % doi)
    return page.geturl()
  except urllib2.HTTPError:
    return None 

def parse_arxiv_abstxt(abstxt):
  # Grab and parse out the arxiv txt format
  # this needs fixing for overflowing of lines
  sections = abstxt.split('\\\\')

  sections[1] = re.sub('\n  ', ' ', sections[1])
  sections[2] = re.sub('\n  ', ' ', sections[2])

  values = dict([(k.lower(), v.strip()) for k, v in re.findall("(.*?):(.*?)\n", sections[1])])
  
  values['abstract'] = sections[2].strip()

  return values

def split_authors(s):
  return [x.strip() for x in re.split(' and |,|:', s)]

def split_categories(s):
  return [x.strip() for x in s.split()]

def parse_date(s):
  dates = re.findall('([0-9]+) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ([0-9]+)', s)
  return " ".join(dates[0])

def build_paper(abstxt):
  abs_values = parse_arxiv_abstxt(abstxt)

  paper = {} 

  paper['title'] = abs_values['title']
  paper['author_names'] = split_authors(abs_values['authors'])
  paper['abstract'] = abs_values['abstract'].replace('\n', ' ')
  paper['arxiv_categories'] = split_categories(abs_values['categories'])
  paper['date_submitted'] = parse_date(abs_values['date'])

  if 'license' in abs_values:
    paper['license'] = abs_values['license']
     
  paper['ids'] = {}
  paper['ids']['arxiv'] = abs_values['arxiv']

  if 'doi' in abs_values:
    paper['ids']['doi'] = abs_values['doi']

  return paper

def scrape(url):
  if '?fmt=txt' not in url:
    url = url + '?fmt=txt'
  urls, response = get_response_chain(url)

  abstxt = response.read()

  paper = build_paper(abstxt)
  paper['source_urls'] = [uri for _, uri in urls] + [url.replace('?fmt=txt', '')]

  return paper

if __name__ == '__main__':
  print scrape(sys.argv[1]) 
