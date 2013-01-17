import scrape_meta_tags as smt
import sys
from utils import *
import time
from dateutil.parser import parse as parse_date
import lxml.html
import re


SCRAPER_DOMAINS = ['http://www.cell.com/home']


def scrape(abstract_url):
    tree, urls, page_text = get_tree(abstract_url) 

    article = smt.scrape(abstract_url)

    ab1 = tree.xpath("//div[@id='load']")[0].text_content()
    ab2 = ab1.split("Summary")[1]
    article['abstract'] =  ab2

    article['scraper'] = 'cell'
    
    return article

if __name__ == "__main__":
  print scrape(sys.argv[1])
