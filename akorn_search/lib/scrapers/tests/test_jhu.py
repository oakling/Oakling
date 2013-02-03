import unittest
import os

from akorn_search.lib.scrapers.journals.scrape_jhu import ScraperJhu
from akorn_search.lib.scrapers.journals.router import discover_scrapers

class JhuScraperTest(unittest.TestCase):

    def test_scraper_added(self):
        scrapers = discover_scrapers()

    def test_journal(self):
        scraper = ScraperJhu()
        file = open(os.path.join(os.path.dirname(__file__), "data", "jhu_ajm.html"))
        page_text = file.read()
        file.close()
        current_issue_url = scraper.scrape_journal(page_text)
        expected_url = 'http://muse.jhu.edu/journals/american_journal_of_mathematics/toc/ajm.134.6.html'
        assert current_issue_url == expected_url

    def test_issue(self):
        scraper = ScraperJhu()
        file = open(os.path.join(os.path.dirname(__file__), "data", "jhu_ajm_issue.html"))
        page_text = file.read()
        file.close()
        article_list = scraper.scrape_issue(page_text)

    def test_article(self):
        scraper = ScraperJhu()
        file = open(os.path.join(os.path.dirname(__file__), "data", "jhu_ajm_article.html"))
        article = file.read()
        file.close()
        new_article = scraper.scrape_article(article)
        new_article['scraper'] == 'jhu'
        new_article['title'] == 'Disk counting on toric varieties via tropical curves'
        new_article['author_names'] == 'Takeo Nishinou', new_article['author_names']
        #new_article['abstract'][:14] == 'In this paper,', new_article['abstract']

