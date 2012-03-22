from lib.scrapers.journals import scrape_pr
from lib.utils import save

def scrape_and_add(url):
    """Scrape the journal page and add to database."""

    #Find the appropriate scraper
    #Call it
    article = scrape_pr(url)
    #Add entry to database
    return save(article)

def merge(new_id, old_ids):
    """Try to merge the two database entries."""
    pass
