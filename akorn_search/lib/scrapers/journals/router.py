import sys, os
import urllib2
import cookielib
import pkgutil
import urlparse
import utils
from utils import RedirectHandler, Ignore401Handler
from couch import db_store, db_journals, db_scrapers

def resolve_doi(doi):
  cookiejar = cookielib.CookieJar()
  req = urllib2.Request('http://dx.doi.org/' + doi, headers=utils.headers)
  urls = []
  opener = urllib2.build_opener(Ignore401Handler(), RedirectHandler(urls),
                                urllib2.HTTPCookieProcessor(cookiejar))
  response = opener.open(req)

  return response.geturl()

def resolve_url(url):
  cookiejar = cookielib.CookieJar()
  req = urllib2.Request(url, headers=utils.headers)
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

