import sys
import urlparse
import couchdb
import urllib2
import cookielib

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

def get_response_chain(req):
  urls = []
  cookiejar = cookielib.CookieJar()
  opener = urllib2.build_opener(RedirectHandler(urls), urllib2.HTTPCookieProcessor(cookiejar))

  response = opener.open(req)

  code = 200 # Not technically correct
  urls.append((code, response.geturl()))
  return (urls, response)

def resolve_doi(doi):
  cookiejar = cookielib.CookieJar()
  req = urllib2.Request('http://dx.doi.org/' + doi, headers=headers)
  urls = []
  opener = urllib2.build_opener(RedirectHandler(urls), urllib2.HTTPCookieProcessor(cookiejar))
  response = opener.open(req)

  return response.geturl()

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
    
    article['scraper_module'] = scraper_doc['module']

    return article

def merge(new_id, old_ids):
    """Try to merge the two database entries."""
    pass
