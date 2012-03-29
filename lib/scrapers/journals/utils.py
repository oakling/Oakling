import sys
from lib.utils import save
import urlparse
import couchdb

class ScraperNotFound(Exception):
  pass

def resolve_scraper(url):
  # Do it by domain for now. This might not always work, a full url prefix might be needed, but this is cheaper.
  url_parsed = urlparse.urlparse(url)
  domain = url_parsed.netloc

  db = couchdb.Server()['scrapers']
  records = db.view('index/domain', key=domain, include_docs='true').rows

  if not records:
    return None
  else:
    return records[0].doc

def load_module(module_path):
    __import__(module_path)
    return sys.modules[module_path]

def resolve_and_scrape(url):
    """Scrape the journal page and add to database."""

    scraper_doc = resolve_scraper(url)

    if scraper_doc is None:
      raise ScraperNotFound(url)
      
    scraper_module = load_module(scraper_doc['module'])
    article = scraper_module.scrape(url)
    
    return article

def merge(new_id, old_ids):
    """Try to merge the two database entries."""
    pass
