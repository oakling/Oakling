from lib.scrapers.journals.utils import make_blank_article as base_make_blank_article

class BaseScraper():
    """Base class for a web scraper"""

    def make_blank_article(self):
        """"Create a blank article ready to be populated"""
        return base_make_blank_article()
