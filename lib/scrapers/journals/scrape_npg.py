import sys
import urllib2
import lxml.html
import urlparse

#DESCRIPTION:
# Scrapes an article from Nature Publishing Group

#TO DO/NOTES:
# Journal is given by full title rather than abbreviation
# Doesnt take full abstract if it contains HTML tags
# Include issns in 'ids'

#JOURNALS:


#WEBSITES:



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
  article['title'] = tree.xpath("//meta[@name='DC.title']/@content")[0]
  article['author_names'] = [author for author in tree.xpath("//meta[@name='DC.creator']/@content")]
  
  article['abstract'] = tree.xpath("//div[@class='content']/p")[0].text_content()

  article['journal'] = tree.xpath("//meta[@name='citation_journal_title']/@content")[0]
  article['volume'] = tree.xpath("//meta[@name='prism.volume']/@content")[0]
  article['page_first'] = tree.xpath("//meta[@name='prism.startingPage']/@content")[0]
  article['page_last'] = tree.xpath("//meta[@name='prism.endingPage']/@content")[0]
  article['ids'] = dict(zip(['doi'], [tree.xpath("//meta[@name='citation_doi']/@content")[0][4:]]))
  
  year = tree.xpath("//meta[@name='citation_date']/@content")
  if year:
    article['publication_year'] = year[0][:4]
  
  for e in article:
	print e, ": ", article[e]
  
  
if __name__ == "__main__":
  print scrape(sys.argv[1])
