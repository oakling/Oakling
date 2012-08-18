import sys
import urlparse
import couchdb
import urllib2
import cookielib
import classification
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',} 

server = couchdb.Server()

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
  db_journals = server['journals']

  matches = db_journals.view('index/aliases', key=alias).rows

  if matches:
    journal_id = matches[0].id
    #cache[journal_name] = journal_id
  else:
    journal_id = None

  return journal_id

def resolve_scraper(url):
  # Do it by domain for now. This might not always work, a full url prefix might be needed, but this is cheaper.

  url_parsed = urlparse.urlparse(url)
  domain = url_parsed.netloc

  db = server['scrapers']
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
      url = resolve_url(url)
      scraper_doc = resolve_scraper(url)
   
      if scraper_doc is None: 
          # default to meta tags
          scraper_doc = {'module': 'lib.scrapers.journals.scrape_meta_tags'}

    scraper_module = load_module(scraper_doc['module'])
      

    article = scraper_module.scrape(url)
    
    article['scraper_module'] = scraper_doc['module']

    if 'journal' in article:
      journal_name = article['journal']
    elif 'citation' in article and 'journal' in article['citation']['journal']:
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

def categorize(codes):
    """Put classification codes into gropus."""
    categories = {}

    for code in codes:
        match = False
        for group in classification.codes:
            matches = re.findall(group[0], code)
            if matches:
                categories.setdefault(group[1], []).extend(matches)
                match = True
        if not match:
            categories.setdefault('unknown', []).append(code)
    return categories
