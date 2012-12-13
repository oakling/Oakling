import sys, os
import urlparse
import couchdb
import urllib2
import cookielib
import classification
import re
import pkgutil

from couch import db_store, db_journals, db_scrapers

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',} 

class ScraperNotFound(Exception):
  pass

def resolve_article(doc, db):
  if 'merged_into' in doc:
    return resolve_article(db[doc['merged_into']])
  else:
    return doc

# This is code to handle chains of redirects. It records each url we're redirected to.
class RedirectHandler(urllib2.HTTPRedirectHandler):
  def __init__(self, accum):
    self.accum = accum

  def redirect_request(self, req, fp, code, msg, headers, newurl):
    self.accum.append((code, newurl))

    return urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)

class Ignore401Handler(urllib2.BaseHandler):
  def http_error_401(self, req, fp, code, msg, hdrs):
    return fp
  
  def http_error_403(self, req, fp, code, msg, hdrs):
    return fp

def get_response_chain(req):
  urls = []
  cookiejar = cookielib.CookieJar()
  opener = urllib2.build_opener(Ignore401Handler(), RedirectHandler(urls),
                                urllib2.HTTPCookieProcessor(cookiejar))

  response = opener.open(req)

  code = 200 # Not technically correct
  urls.append((code, response.geturl()))
  return (urls, response)

def resolve_doi(doi):
  cookiejar = cookielib.CookieJar()
  req = urllib2.Request('http://dx.doi.org/' + doi, headers=headers)
  urls = []
  opener = urllib2.build_opener(Ignore401Handler(), RedirectHandler(urls),
                                urllib2.HTTPCookieProcessor(cookiejar))
  response = opener.open(req)

  return response.geturl()

def resolve_url(url):
  cookiejar = cookielib.CookieJar()
  req = urllib2.Request(url, headers=headers)
  urls = []
  opener = urllib2.build_opener(Ignore401Handler(), RedirectHandler(urls),
                                urllib2.HTTPCookieProcessor(cookiejar))
  response = opener.open(req)

  return response.geturl()

def resolve_journal(alias):
  matches = db_journals.view('index/aliases', key=alias).rows

  if matches:
    journal_id = matches[0].id
    #cache[journal_name] = journal_id
  else:
    journal_id = None

  return journal_id

def load_module(module_path):
    __import__(module_path)
    return sys.modules[module_path]

def discover_scrapers():
  """
    Use pkgutil to find scrapers in this module. Build a list of scrapers and which domains they map to.
  """

  scraper_modules = []
  scraper_domain_map = {}

  d = os.path.dirname(__file__)

  for module_importer, name, ispkg in pkgutil.iter_modules([d,]):
    if not name.startswith('scrape_'):
      continue
    module = module_importer.find_module(name).load_module(name)

    scraper_modules.append(module)

    if hasattr(module, 'SCRAPER_DOMAINS'):
      for domain in module.SCRAPER_DOMAINS:
        scraper_domain_map[domain] = module

  return (scraper_modules, scraper_domain_map)

scraper_modules, scraper_domain_map = discover_scrapers()

def resolve_scraper(url):
  # Do it by domain for now. This might not always work, a full url prefix might be needed, but this is cheaper.
  url_parsed = urlparse.urlparse(url)
  domain = url_parsed.netloc

  #records = db_scrapers.view('index/domain', key=domain, include_docs='true').rows

  #if not records:
  #  return None
  #else:
  #  return records[0].doc

  print domain

  if domain in scraper_domain_map:
    return scraper_domain_map[domain]
  else:
    return None

def resolve_and_scrape(url):
    """Scrape the journal page and add to database."""

    scraper_module = resolve_scraper(url)

    if scraper_module is None:
      url = resolve_url(url)
      scraper_module = resolve_scraper(url)
   
      if scraper_module is None: 
          # default to meta tags
          scraper_module = load_module('lib.scrapers.journals.scrape_meta_tags')

    module_path = "lib.scrapers.journals." + scraper_module.__name__

    print module_path

    article = scraper_module.scrape(url)
    
    article['scraper_module'] = module_path 

    if 'journal' in article:
      journal_name = article['journal']
    elif 'citation' in article and 'journal' in article['citation']:
      journal_name = article['citation']['journal']
    elif 'categories' in article and 'arxiv' in article['categories']:
      journal_name = 'arxiv:' + article['categories']['arxiv'][0]
    else:
      journal_name = None

    if journal_name:
      journal_id = resolve_journal(journal_name)

      if journal_id:
        article['journal_id'] = journal_id

    return article

def merge(new_id, old_ids):
    """Try to merge the two database entries."""
    pass

if __name__ == "__main__":
  print resolve_and_scrape(sys.argv[1])
