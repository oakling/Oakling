import sys
import lxml.html
import re
from utils import *

SCRAPER_DOMAINS = ['www.mitpressjournals.org',]

# Tested on:
# - Neural Computation

def scrape(abstract_url):
  tree, urls, page_text = get_tree(abstract_url)

  article = make_blank_article()
  article['scraper'] = 'MIT'
  article['source_urls'] = [uri for _, uri in urls]

  article['title'] = get_meta('dc.Title', tree)
  article['publisher'] = get_meta('dc.Publisher', tree).strip()
  article['author_names'] = get_meta_list('dc.Creator', tree)

  # Two identifier schemes used --- do we want both?
  article['ids'] = dict(zip(['publisher-id','doi'], get_meta_list('dc.Identifier', tree)))

  article['journal'] = tree.xpath("//h1[@class='journalTitle']/a/img/@alt")[0]

  # dc.Description is present, but contains an abbreviated abstract
  # --- this gets the full abstract
  article['abstract'] = tree.xpath("//div[@class='abstractSection']/p/text()")[0]

  article['citation']['journal'] = article['journal']

  # Citation details (volume, number, pages) given as text
  # immediately following the h1 tag.
  # example: December 2012, Vol. 24, No. 2, Pages 1-35

  citation_text = tree.xpath("//h1[@class='journalTitle']/following-sibling::text()")[0]

  pub_year, volume, number, page_first, page_last = re.findall('\d+', citation_text)

  article['citation'] = {}
  article['citation']['volume'] = volume
  article['citation']['number'] = number
  article['citation']['page_first'] = page_first
  article['citation']['page_last'] = page_last

  date = get_meta('dc.Date', tree).split('-')
  if date:
    article['date_published'] = make_datestamp(date[2], date[1], date[0])
    article['citation']['year'] = date[0]

  return article

if __name__ == "__main__":
  print scrape(sys.argv[1])

