from celery.task import task
from lib.scrapers.journals.tasks import scrape_journal
from lib.scrapers.feeds import aps_feed_scraper
import feedparser

APS_FEEDS = [
    "http://feeds.aps.org/rss/recent/prl.xml",
    "http://feeds.aps.org/rss/recent/pra.xml",
    "http://feeds.aps.org/rss/recent/prb.xml",
    "http://feeds.aps.org/rss/recent/prc.xml",
    "http://feeds.aps.org/rss/recent/prd.xml",
    "http://feeds.aps.org/rss/recent/pre.xml",
    "http://feeds.aps.org/rss/recent/prx.xml",
]


@task
def fetch_APS_feeds():
    for feed_url in APS_FEEDS:
        add_feed_items.delay(feed_url)

@task
def add_feed_items(url):
    """Add feed items to database.."""

    #Figure out what type of feed it is (based on url)
    feed_scraper = aps_feed_scraper

    # should be smarter here, e.g. use If-Modified-Since
    feed = feedparser.parse(url)

    # FEED may already contain enough information
    for item in feed['items']:
        scrape_journal.delay(feed_scraper.url(item),
                             feed_scraper.identifier(item))
                            
