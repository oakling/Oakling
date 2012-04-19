from lib.utils import save
import urls
import re

def scrape(url):
    for pattern, scraper in urls.urls:
        if re.search(pattern, url):
            if not hasattr(scraper, 'scrape'):
                scraper = __import__(scraper, fromlist=['scrape'])
            return scraper.scrape(url)
    # raise an error here

def scrape_and_add(url):
    """Scrape the journal page and add to database."""

    article = scrape(url)
    #Add entry to database
    return save(article)

def link(new_id, old_ids):
    """Create links between entries."""
    pass
