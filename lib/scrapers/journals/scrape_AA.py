import sys
import lxml.html
import utils
#from comm import *
import urllib2
import time
import datetime

#DESCRIPTION:
# Scrapes an article from Astronomy & Astrophysics RSS feeds:
# http://www.aanda.org/

#TO DO/NOTES:
# Journal is given by full title rather than abbreviation

#JOURNALS:
# Astronomy & Astrophysics

#WEBSITES:
# feed://www.aanda.org/articles/aa/rss/TOCRSS/rss.xml


months = {'January':1, 'February':2, 'March':3, 'April':4,\
          'May':5, 'June':6, 'July':7, 'August':8, 'September':9,\
          'October':10, 'November':11, 'December':12}


def get_tree(abstract_url):
    req = urllib2.Request(abstract_url, headers=utils.headers)
    urls, page = utils.get_response_chain(req)
    page_text = page.read().decode('utf-8')

    tree = lxml.html.fromstring(page_text, base_url=page.geturl())

    return tree, urls, page_text

def make_blank_article():
    article = {'scraper': None, 'source_urls': None, 'title': None, 'author_names': None,
               'ids': None, 'citation': None, 'date_published': None, 'abstract': None,
               'journal': None, }

    article['citation'] = { 'journal':None, 'volume': None, 'year': None, 'page': None, }

    return article

def get_div(name, tree):
    attribute = tree.xpath("//div[@name='%s']/@content" % name)
	
    if attribute:
      return attribute[0]
    else:
      return None

def scrape(abstract_url):
    tree, urls, page_text = get_tree(abstract_url)

    article = make_blank_article()
    article['scraper'] = 'AA'
    article['source_urls'] = [uri for _, uri in urls]
    
    try:
        article['title'] = tree.xpath("//div[@id='head']/h2")[0].text_content()
    except:
        pass

    article['author_names'] = tree.xpath("//div[@id='head']/p")[0].text_content()
    
    article['journal'] = tree.xpath("//meta[@name='keywords']/@content")[0].split(',')[0]
    
    info = tree.xpath("//div[@id='head']//p[@class='history']")[0].text_content()
    pubdate = info.split(' ')[4:]
    pubdate[1] = months[pubdate[1]]
    day, month, year = int(pubdate[0]), int(pubdate[1]), int(pubdate[2])
    pubdateuni = time.mktime(datetime.date(year, month, day).timetuple())
    article['date_published'] = pubdateuni


    return article
