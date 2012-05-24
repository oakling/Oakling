import sys
import urllib2
import lxml.html
import urlparse
import utils
import datetime
import time

#DESCRIPTION:
# Scrapes an article from IOP Science (Full list: http://iopscience.iop.org/journals)

#TO DO/NOTES:
# Journal is given by full title rather than abbreviation
# Doesnt take full abstract if it contains HTML tags

#JOURNALS:


#WEBSITES:


def get_tree(response):
  return lxml.html.parse(response.read().decode('utf-8'),
                         base_url=response.geturl())


# Scrape the given url
def scrape(abstract_url):
  req = urllib2.Request(abstract_url)
  urls, page = utils.get_response_chain(req)

  # Parse the HTML into a tree we can query
  page_text = page.read().decode('utf-8')
  tree = lxml.html.fromstring(page_text, base_url=abstract_url)

  article = {}
  
  article['source_urls'] = [uri for _, uri in urls]
  article['title'] = tree.xpath("//meta[@name='dc.title']/@content")[0]
  article['author_names'] = [author for author in
                             tree.xpath("//meta[@name='dc.creator']/@content")]
  article['abstract'] = tree.xpath("//meta[@name='dc.description']/@content")[0]
  
  article['journal'] = tree.xpath("//meta[@name='citation_journal_title']/@content")[0]
  article['citation'] = {'journal': tree.xpath("//meta[@name='citation_journal_title']/@content")[0],
                         'volume': tree.xpath("//meta[@name='citation_volume']/@content")[0],
                         'page_first': tree.xpath("//meta[@name='citation_firstpage']/@content")[0],}


  article['ids'] = dict(zip(['doi'], [tree.xpath("//meta[@name='citation_doi']/@content")[0]]))
  
  year = tree.xpath("//meta[@name='citation_date']/@content")
  if year:
    article['citation']['pub_year'] = year[0][:4]
  
  return article  
  
if __name__ == "__main__":
  print scrape(sys.argv[1])

