from lxml import html

from utils import get_meta
from utils import get_meta_list
from base import BaseScraper

SCRAPER_DOMAINS = ['muse.jhu.edu',]

class ScraperJhu(BaseScraper):
    """Scrape JHU for the American Journal of Mathematics"""

    def scrape_issue(self, page_text=None):
        """Scrape a html page which is an issue of the journal"""
        if page_text is None:
            return None
        tree = html.fromstring(page_text)
        name = 'current'
        attribute = tree.cssselect('div.current a')
        current_issue_url = attribute[0].attrib['href']
        return current_issue_url

    def scrape_article(self, page_text=None):
        """Scrape a html page which is an issue of the journal"""
        if page_text is None:
            return None
        tree = html.fromstring(page_text)
        article = self.make_blank_article()
        article['scraper'] = 'jhu'
        article['source_urls'] = ''
        article['publisher'] = ''
        article['title'] = get_meta('article-title', tree)
        article['author_names'] = get_meta_list('contrib', tree)
        article['abstract'] =  get_meta('abstract', tree)
        article['journal'] = ''
        article['date_published'] = ''
        article['citation']['journal'] = ''
        article['citation']['volume'] = ''
        article['citation']['page'] = ''
        article['citation']['year'] = ''
        article['ids'] = ''
        return article

