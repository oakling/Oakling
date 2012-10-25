import sys
import lxml.html
import utils
from comm import *

#DESCRIPTION:
# Scrapes an article from MNRAS: http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-2966
# RSS feed at: feed://onlinelibrary.wiley.com/rss/journal/10.1111/(ISSN)1365-2966

#TO DO/NOTES:
# Journal is given by full title rather than abbreviation
#SOME WILEY JOURNALS HAVE id="graphicalAbstract" SO MUST FACTOR TIHS IN WITH A TRY EXCEPT!!!

#JOURNALS:
#Monthly Notices of the Royal Astronomical Society
#Seems to work for any on Wiley Online

#WEBSITES:


def scrape(abstract_url):
  tree, urls, page_text = get_tree(abstract_url) 

  article = make_blank_article()
  article['scraper'] = 'wiley'
  article['source_urls'] = [uri for _, uri in urls]

  #article['publisher'] = get_meta('citation_publisher', tree)

  article['journal'] = get_meta('citation_journal_title', tree)

  article['title'] = get_meta('citation_title', tree)

  article['ids'] = dict(zip(['doi'], [get_meta('citation_doi', tree)]))

  article['author_names'] = get_meta_list('citation_author', tree)
  
 # article['abstract'] = tree.xpath("//div[@id='abstract']/div/p")[0].text_content()

  article['date_published'] = get_meta('citation_publication_date', tree)

  article['citation']['journal'] = article['journal']
  article['citation']['volume'] = get_meta('citation_volume', tree)
  article['citation']['year'] = article['date_published'].split('/')[0]

  return article

if __name__=="__main__":
    print scrape(sys.argv[1])

  

  
