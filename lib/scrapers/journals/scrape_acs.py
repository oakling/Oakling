import sys
import urllib2
import lxml.html
import urlparse

from utils import get_response_chain

#DESCRIPTION:
# Scrapes all journal articles from ACS publishing (American Chemical Society) given the URL of the abstract


#TO DO:
# The abstract contained in the meta element is not necessarily complete if it is particularly long. Could take "//div[@id='abstractBox']/p" instead, however this can contain HTML formatting.
# Deal with escaped unicode characters e.g. '\U011f' in text



#WEBSITES:
# http://pubs.acs.org/

def get_tree(response):
  return lxml.html.parse(response, base_url=response.geturl())
    
# Scrape the given url
def scrape(abstract_url):
  source_urls, response = get_response_chain(abstract_url)

  tree = get_tree(response)  

  article = {}
  
  article['source_urls'] = [url for code, url in source_urls]
  article['title'] = tree.xpath("//meta[@name='dc.Title']/@content")[0]
  article['author_names'] = [author for author in tree.xpath("//meta[@name='dc.Creator']/@content")]
  article['citation'] = {'journal': tree.xpath("//div[@id='citation']/cite")[0].text}
  article['ids'] = {'doi': tree.xpath("//meta[@name='dc.Identifier']/@content")[0]}
	
  # Some old (pre-internet) articles may not have an abstract
  abstract = tree.xpath("//meta[@name='dc.Description']/@content")
  if abstract:
    article['abstract'] = abstract[0]

  # If an article is 'ASAP' (advance web preview) it will not yet have a publication year
  year = tree.xpath("//span[@class='citation_year']")
  if year:
    article['citation']['pub_year'] = year[0].text
	
  return article

if __name__ == "__main__":
  print scrape(sys.argv[1])
