import couchdb
from celery.task import task
from lib.scrapers.journals.tasks import scrape_journal
from lib.scrapers.feeds import aps_feed_scraper
import feedparser

@task
def fetch_feeds():
    # get list of feed urls from couchdb called feeds
    couch = couchdb.Couch()
    db = couch['feeds']

    feeds = db.query("""function(doc){
                            if (doc.url){ 
                                emit(doc.url, null);
                            }}:""")
    for feed_url in [feed['key'] for feed in feeds.rows]:
        add_feed_items.delay(feed_url)

@task
def add_feed_items(url):
    """Add feed items to database.."""

    #Figure out what type of feed it is (based on url)
    feed_scraper = aps_feed_scraper

    # should be smarter here, e.g. use If-Modified-Since
    feed = feedparser.parse(url)

    for item in feed['items']:
        scrape_journal.delay(feed_scraper.url(item),
                             feed_scraper.identifier(item))
                            
