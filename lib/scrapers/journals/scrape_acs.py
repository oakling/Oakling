import sys
import lxml.html
import lib.scrapers.journals.utils as utils
import re

SCRAPER_DOMAINS = ['pubs.acs.org',]

#WEBSITES:
# http://pubs.acs.org/


def scrape(abstract_url):
  tree, urls, page_text = utils.get_tree(abstract_url) 

  article = make_blank_article()
  article['scraper'] = 'acs'
  article['source_urls'] = [uri for _, uri in urls]

  article['title'] = utils.get_meta('dc.Title', tree)
  article['publisher'] = utils.get_meta('dc.Publisher', tree)
  article['author_names'] = utils.get_meta_list('dc.Creator', tree)

  article['ids'] = dict(zip(['doi'], [utils.get_meta('dc.Identifier', tree)]))

  try:
      article['journal'] = tree.xpath("//div[@id='journalTop']/div/a/img/@alt")[0]
  except:
      pass

  try:
      article['abstract'] = tree.xpath("//div[@id='abstractBox']/p")[0].text_content()
  except:
      pass

  try:
      article['citation']['journal'] = tree.xpath("//div[@id='citation']/cite")[0].text
  except:
      pass

  try:
      article['citation']['volume'] = tree.xpath("//span[@class='citation_volume']")[0].text
  except:
      pass

  page_cite = tree.xpath("//div[@id='citation']")
  if page_cite:
      page = re.findall('pp\s([0-9]+)', page_cite[0].text_content())
      if page:
          article['citation']['page'] = page[0]

  date = utils.get_meta('dc.Date', tree).split()
  if date:
      article['date_published'] = utils.make_datestamp(date[1][:-1], months[date[0]], date[2])
      article['citation']['year'] = date[2]


	
  return article

if __name__ == "__main__":
  print scrape(sys.argv[1])

