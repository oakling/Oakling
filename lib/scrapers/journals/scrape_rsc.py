import sys
import lxml.html
from utils import *

SCRAPER_DOMAINS = ['pubs.rsc.org',]

#JOURNALS:

#WEBSITES:
# http://pubs.rsc.org


def scrape(abstract_url):
  tree, urls, page_text = get_tree(abstract_url) 

  article = make_blank_article()
  article['scraper'] = 'rsc'
  article['source_urls'] = [uri for _, uri in urls]
  article['ids'] = {'doi': get_meta('DC.Identifier', tree), }  

  article['title'] = get_meta('DC.title', tree)
  article['publisher'] = get_meta('DC.publisher', tree)
  article['author_names'] = get_meta_list('DC.Creator', tree)

  try:
      article['journal'] = tree.xpath("//img[@id='imgLoader']/@title")[0]
  except:
      pass

  try:
      article['abstract'] = tree.xpath("//p[@xmlns='http://www.rsc.org/schema/rscart38']")[0].text_content()
  except:
      pass
  
  article['citation']['journal'] = get_meta('citation_journal_title', tree)
  article['citation']['volume'] = get_meta('citation_volume', tree)
  article['citation']['page'] = get_meta('citation_firstpage', tree)

  pub_date = get_meta('citation_publication_date', tree)
  if pub_date:
    split = pub_date.split('-')
    article['date_published'] = make_datestamp(split[2], split[1], split[0])
    article['citation']['year'] = split[0]

  return article
  
  
