import sys
import urllib2
import lxml.html
import urlparse
import utils

#DESCRIPTION:
# Scrapes an article from ASBMB and NAS given a URL

#TO DO:
# Include issns in 'ids'
# Abstract contains a lot of whitespace: remove this
# Doesnt take full abstract if it contains HTML tags


#JOURNALS:
# Publisher: National Academy of Sciences
#   Proceedings of the National Academy of Sciences; PNAS
# Publisher: American Society for Biochemistry and Molecular Biology
#   Journal of Biological Chemistry; J. Biol. Chem.
#   Molecular & Cellular Proteomics; Mol Cell Proteomics
#   Journal of Lipid Research; J. Lipid Res.

#WEBSITES:
# http://www.pnas.org/
# http://www.jbc.org/
# http://www.mcponline.org/
# http://www.jlr.org/


def get_tree(response):
  return lxml.html.parse(response, base_url=response.geturl())

# Scrape the given url
def scrape(abstract_url):
  req = urllib2.Request(abstract_url, headers=utils.headers)
  urls, response = utils.get_response_chain(req)
  tree = get_tree(response)

  article = {}
  
  article['source_urls'] = [uri for _, uri in urls]
  article['title'] = tree.xpath("//meta[@name='DC.Title']/@content")[0]
  article['author_names'] = [author for author in tree.xpath("//meta[@name='DC.Contributor']/@content")]
  article['abstract'] = tree.xpath("//div[@class='section abstract']")[0].text_content().replace('\n                  Abstract\n                  ', '').replace('\n                     ', ' ').strip()
  
  article['citation'] = {'journal': tree.xpath("//meta[@name='citation_journal_abbrev']/@content")[0],
                         'volume': tree.xpath("//meta[@name='citation_volume']/@content")[0],
                         'page_first': tree.xpath("//meta[@name='citation_firstpage']/@content")[0],
                         'page_last': tree.xpath("//meta[@name='citation_lastpage']/@content")[0],}

  article['ids'] = {'doi': tree.xpath("//meta[@name='DC.Identifier']/@content")[0],}
  
  year = tree.xpath("//meta[@name='citation_date']/@content")
  if year:
    article['citation']['pub_year'] = year[0][-4:]
  
  return article 
  
if __name__ == "__main__":
  print scrape(sys.argv[1])
