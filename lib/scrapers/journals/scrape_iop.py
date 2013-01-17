import sys
import lxml.html
from utils import *

SCRAPER_MODULES = ['iopscience.iop.org',]

#DESCRIPTION:
# Scrapes an article from IOP Science (Full list: http://iopscience.iop.org/journals)

#TO DO/NOTES:
# Journal is given by full title rather than abbreviation

#JOURNALS:


#WEBSITES:


def scrape(abstract_url):
  tree, urls, page_text = get_tree(abstract_url) 

  article = make_blank_article()
  article['scraper'] = 'iop'
  article['source_urls'] = [uri for _, uri in urls]

  article['publisher'] = get_meta('citation_publisher', tree)

  article['title'] = get_meta('dc.title', tree)
  if article['title'] == None:
    article['title'] = get_meta('dc.Title', tree)


  article['author_names'] = get_meta_list('dc.creator', tree)
  if article['author_names'] == None:
    article['author_names'] = get_meta_list('dc.contributor', tree)

  article['abstract'] = get_meta('dc.description', tree)
  
  article['journal'] = get_meta('citation_journal_title', tree)

  article['citation']['journal'] = get_meta('citation_journal_abbrev', tree)
  article['citation']['volume'] = get_meta('citation_volume', tree)
  article['citation']['page'] = get_meta('citation_firstpage', tree)

  article['ids'] = dict(zip(['doi'], [get_meta('citation_doi', tree)]))
 
  pub_date = get_meta('citation_publication_date', tree)
  if pub_date:
    split = pub_date.split('-')
    article['date_published'] = make_datestamp(split[2], split[1], split[0])
    article['citation']['year'] = split[0]

  return article 
  
if __name__ == "__main__":
  print scrape(sys.argv[1])

