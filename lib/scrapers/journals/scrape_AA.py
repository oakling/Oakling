import sys
import lxml.html
import utils
from comm import *
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



    info = tree.xpath("//div[@id='head']")[0].text_content()

    ab1 = info.split("Abstract")[1]
    ab2 = ab1.split("Key words")[0]
    article['abstract'] = ab2

    rec1 = info.split("Accepted: ")[1]
    rec2 = rec1.split("\nAbstract")[0]

    day, month, year = rec2.split(' ')
    article['date_published'] = make_datestamp(day, months[month], year)

    article['citation']['year'] = year

    issueinfo = info.split(article['title'])[0]
    jour, vol, num, yea = issueinfo.split(' ')[0], issueinfo.split(' ')[1],\
                          issueinfo.split(' ')[2], issueinfo.split(' ')[3]

    article['citation']['journal'] = jour
    article['citation']['volume'] = vol.split(',')[0]

    doi = article['source_urls'][0].split('doi=')[1]
    doi2 = doi.split('&')[0]
    article['ids'] = doi2


    return article
