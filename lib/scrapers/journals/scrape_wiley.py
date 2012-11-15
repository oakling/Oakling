import sys
import lxml.html
import utils
from comm import *
import time
import datetime

#DESCRIPTION:
# Scrapes an article from Wiley Online RSS feeds:
# http://onlinelibrary.wiley.com/browse/publications?type=journal&activeLetter=

#TO DO/NOTES:
# Journal is given by full title rather than abbreviation

#JOURNALS:
#Monthly Notices of the Royal Astronomical Society
#Seems to work for any on Wiley Online webpages

#WEBSITES:

def fix_wiley_url(url):
  # Fix issue with session key being appended, thus mucking up duplicate spotting
  return url.split(';')[0]

def scrape(abstract_url):
  abstract_url = fix_wiley_url(abstract_url)
  tree, urls, page_text = get_tree(abstract_url) 

  article = make_blank_article()
  article['scraper'] = 'wiley'
  article['source_urls'] = [uri for _, uri in urls]

  try:
    article['journal'] = get_meta('citation_journal_title', tree)
  except:
    pass
  try:
    article['title'] = get_meta('citation_title', tree)
  except:
    pass
  try:
    article['ids'] = dict(zip(['doi'], [get_meta('citation_doi', tree)]))
  except:
    pass
  try:
    article['author_names'] = get_meta_list('citation_author', tree)
  except:
    pass
  try:
    article['abstract'] = tree.xpath("//div[@id='abstract']/div/p")[0].text_content()
  except:
    article['abstract'] = tree.xpath("//div[@id='graphicalAbstract']/div/p")[0].text_content()
    
  x = get_meta('citation_publication_date', tree)
  if x is None:
    x = get_meta('citation_online_date', tree)
  

  year, month, day = x.split('/')
  new_date = make_datestamp(day, month, year)
  article['date_published'] = new_date

  
  article['citation']['journal'] = article['journal']
  article['citation']['volume'] = get_meta('citation_volume', tree)
  try:
    article['citation']['year'] = year
  except:
    pass
  
  first_page = get_meta('citation_firstpage', tree)
  if first_page == None:
    first_page = '0'
  
  last_page = get_meta('citation_lastpage', tree)
  if last_page == None:
    last_page = '0'
    
  if first_page != '0' and last_page != '0':
    article['citation']['page'] = first_page + '-' + last_page
    
  return article

#Test
if __name__=="__main__":
    print scrape(sys.argv[1])

  

  
