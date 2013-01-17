import scrape_npg as sn
import sys
from utils import *

SCRAPER_DOMAINS = ['http://www.nature.com/onc/index.html',
                   'http://www.nature.com/embor/index.html',
                   'http://www.nature.com/emboj/index.html']


def scrape(abstract_url):
    tree, urls, page_text = get_tree(abstract_url)

    article = sn.scrape(abstract_url)

    article['abstract'] = None

    if article['journal'] == 'The EMBO Journal':
        try:
            article['abstract'] = tree.xpath("//p[@class='lead']")[0].text_content()
        except:
            pass

        
    elif article['journal'] == 'EMBO reports':
        try:
            article['abstract'] = tree.xpath("//p[@class='lead']")[0].text_content()
        except:
            pass

    elif article['journal'] == 'Oncogene':
        try:
            article['abstract'] = tree.xpath("//p[@class='abs lead']")[0].text_content()
        except:
            pass
        
        
    return article

if __name__=="__main__":
    print scrape(sys.argv[1])

