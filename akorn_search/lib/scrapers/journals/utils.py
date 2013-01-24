import sys, os
import urlparse
import couchdb
import urllib2
import classification
import cookielib
import re
import lxml.html
import datetime
import time

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


def merge(new_id, old_ids):
    """Try to merge the two database entries."""
    pass

months = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}

def get_tree(abstract_url):
    req = urllib2.Request(abstract_url, headers=headers)
    urls, page = get_response_chain(req)
    page_text = page.read().decode('utf-8')

    tree = lxml.html.fromstring(page_text, base_url=page.geturl())

    return tree, urls, page_text

def strip_space(string):
  newstr= ''
  
  for word in string.split():
    newstr = newstr + ' ' + word
	
  return newstr.lstrip()

def get_meta(name, tree):
    attribute = tree.xpath("//meta[@name='%s']/@content" % name)
	
    if attribute:
      return attribute[0]
    else:
      return None

def get_meta_list(name, tree):
    attributes = tree.xpath("//meta[@name='%s']/@content" % name)
	
    if attributes:
      return [attribute for attribute in attributes]
    else:
	  return None

def make_datestamp(day, month, year):
    day = int(day)
    month = int(month)
    year = int(year)
    return time.mktime(datetime.date(year, month, day).timetuple())

def make_blank_article():
    article = {'scraper': None, 'source_urls': None, 'title': None, 'author_names': None,
               'ids': None, 'citation': None, 'date_published': None, 'abstract': None,
               'journal': None, }

    article['citation'] = { 'journal':None, 'volume': None, 'year': None, 'page': None, }

    return article
    


if __name__ == "__main__":
  print resolve_and_scrape(sys.argv[1])

