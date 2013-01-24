import lxml.html
import urllib2
import datetime
import time

months = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}

def get_tree(abstract_url):
    req = urllib2.Request(abstract_url, headers=utils.headers)
    urls, page = utils.get_response_chain(req)
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
    












