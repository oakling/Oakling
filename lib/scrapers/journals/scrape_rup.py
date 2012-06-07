import sys
import lxml.html
import utils
from comm import *

#NOTES:
#functionally identical to nas scraper - consider merge

#WEBSITES:
# Rockefeller University Press
# http://jcb.rupress.org - The Journal of Cell Biology
# http://jem.rupress.org - The Journal of Experimental Medicine
# http://jgp.rupress.org - The Journal of General Physiology

# Cold Spring Harbor Press
# http://.cshlp.org/


# The American Association of Immunologists
# http://www.jimmunol.org - The Journal of Immunology

# National Academy of Sciences
# http://www.pnas.org/
# http://www.jbc.org/
# http://www.mcponline.org/
# http://www.jlr.org/

# American Association for the Advancement of Science
# http://www.sciencemag.org - Science



def scrape(abstract_url):
  tree, urls, page_text = get_tree(abstract_url) 

  article = make_blank_article()
  article['scraper'] = 'rup'
  article['source_urls'] = [uri for _, uri in urls]

  article['title'] = get_meta('DC.Title', tree)
  article['journal'] = get_meta('citation_journal_title', tree)
  article['publisher'] = get_meta('DC.Publisher', tree)
  article['author_names'] = get_meta_list('DC.Contributor', tree)

  article['abstract'] = strip_space( tree.xpath("//div[@class='section abstract']/p")[0].text_content() )

  article['citation']['journal'] = get_meta('citation_journal_abbrev', tree)
  article['citation']['volume'] = get_meta('citation_volume', tree)
  article['citation']['page'] = get_meta('citation_firstpage', tree)

  article['ids'] = {'doi':get_meta('DC.Identifier', tree),}
  
  pub_date = get_meta('DC.Date', tree)
  if pub_date:
    split = pub_date.split('-')
    article['date_published'] = make_datestamp(split[2], split[1], split[0])
    article['citation']['year'] = split[0]
  
  return article

if __name__ == "__main__":
  print scrape(sys.argv[1])
