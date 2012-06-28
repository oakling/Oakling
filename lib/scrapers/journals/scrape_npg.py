import sys
import urllib2
import lxml.html
import urlparse
import gzip
from comm import *
from StringIO import StringIO

import utils
#DESCRIPTION:
# Scrapes an article from Nature Publishing Group

#TO DO/NOTES:
# Journal is given by full title rather than abbreviation
# Doesnt take full abstract if it contains HTML tags
# Include issns in 'ids'

#JOURNALS:

#WEBSITES:
    
# Scrape the given url
def scrape(abstract_url):
  req = urllib2.Request(abstract_url, headers=utils.headers)
  urls, response = utils.get_response_chain(req)

  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO( response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
  else:
    data = response.read()

  page_text = data.decode('utf-8')
  tree = lxml.html.fromstring(page_text) 

  article = make_blank_article()
  article['scraper'] = 'npg'
  article['source_urls'] = [uri for _, uri in urls]

  article['title'] = get_meta('DC.title',tree)
  if article['title'] == None:
      article['title'] = get_meta('dc.title',tree)

  article['publisher'] = get_meta('DC.publisher',tree)
  if article['publisher'] == None:
      article['publisher'] = get_meta('dc.publisher',tree)

  article['author_names'] = get_meta_list('DC.creator',tree)
  if article['author_names'] == None:
      article['author_names'] = get_meta_list('dc.creator',tree)
  
  article['abstract'] = get_meta('description', tree)
  if not article['abstract']: 
      try:
          article['abstract'] = tree.xpath("//div[@class='content']/p")[0].text_content()
      except:
          pass
  if not article['abstract']: 
      try:
          article['abstract'] = tree.xpath("//div[@id='abs']/p")[0].text_content()
      except:
          pass


  article['citation']['journal'] = get_meta('citation_journal_title', tree)
  article['citation']['volume'] = get_meta('prism.volume', tree)
  article['citation']['page'] = get_meta('prism.startingPage', tree)

  article['journal'] = get_meta('prism.publicationName', tree)

  year = get_meta('citation_date', tree)
  if year:
    article['citation']['year'] = year[0][:4]

  article['ids'] = dict(zip(['doi'], [tree.xpath("//meta[@name='citation_doi']/@content")[0][4:]]))

  pub_date = get_meta('DC.date', tree)
  if pub_date == None:
      pub_date = get_meta('dc.date', tree)

  if pub_date:
      split = pub_date.split('-')
      article['date_published'] = make_datestamp(split[2], split[1], split[0])

  return article

if __name__ == "__main__":
    print scrape(sys.argv[1])
