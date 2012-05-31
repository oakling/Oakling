import sys
import urllib2
import lxml.html
import urlparse
import gzip
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

  article = {}
  
  article['source_urls'] = [uri for _, uri in urls]
  article['title'] = tree.xpath("//meta[@name='DC.title']/@content")[0]
  article['author_names'] = [author for author in tree.xpath("//meta[@name='DC.creator']/@content")]
  
  article['abstract'] = tree.xpath("//div[@class='content']/p")[0].text_content()

  article['citation'] = {}

  article['citation']['journal'] = tree.xpath("//meta[@name='citation_journal_title']/@content")[0]
  article['citation']['volume'] = tree.xpath("//meta[@name='prism.volume']/@content")[0]
  article['citation']['page'] = tree.xpath("//meta[@name='prism.startingPage']/@content")[0]
  article['citation']['page_last'] = tree.xpath("//meta[@name='prism.endingPage']/@content")[0]

  year = tree.xpath("//meta[@name='citation_date']/@content")
  if year:
    article['citation']['year'] = year[0][:4]

  article['ids'] = dict(zip(['doi'], [tree.xpath("//meta[@name='citation_doi']/@content")[0][4:]]))
  
  def make_datestamp(date):
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    return time.mktime(datetime.date(year, month, day).timetuple())
 
  pub_date = tree.xpath("//meta[@name='dc.date']/@content")
  if pub_date:
    article['date_published'] = make_datestamp(pub_date[0].split('-'))

  return article
  
if __name__ == "__main__":
  print scrape(sys.argv[1])
