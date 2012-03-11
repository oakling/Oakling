import sys
import urllib2
import lxml.html
import urlparse

#DESCRIPTION:
# Scrapes all journal articles from ACS publishing (American Chemical Society) given the URL of the abstract


#TO DO:
# The abstract contained in the meta element is not necessarily complete if it is particularly long. Could take "//div[@id='abstractBox']/p" instead, however this can contain HTML formatting.
# Deal with escaped unicode characters e.g. '\U011f' in text



#WEBSITES:
# http://pubs.acs.org/



def get_tree(abstract_url):
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',} 
  page_req = urllib2.Request(abstract_url, headers=headers)
  page = urllib2.urlopen(page_req)
  return lxml.html.parse(page, base_url=abstract_url)

    
# Scrape the given url
def scrape(abstract_url):
  tree = get_tree(abstract_url)  

  article = {}
  
  article['source_url'] = abstract_url
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
