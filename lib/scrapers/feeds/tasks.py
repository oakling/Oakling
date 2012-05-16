from celery.task import task
from lib.scrapers.journals.tasks import scrape_journal
from lib.scrapers.feeds import feed_handlers
import feedparser

@task
def fetch_feed(feedhandler, feed_urls):
    for feed_url in feed_urls:
        add_feed_items.delay(feedhandler, feed_url)

@task
def add_feed_items(feedhandler, feed_url):
    """Add feed items to database.."""

    # should be smarter here, e.g. use If-Modified-Since
    feed = feedparser.parse(feed_url)

    if feedhandler in feed_handlers.handlers:
        handler = feed_handlers.handlers[feedhandler]
    else:
        handler = feed_handlers.handlers['default']

    for item in feed['items']:
        scrape_journal.delay(handler['url'](item))
                             #handler['identifier'](item))
