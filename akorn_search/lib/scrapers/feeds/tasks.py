from celery.task import task
from lib.scrapers.journals.tasks import scrape_journal
from lib.scrapers.feeds import feed_handlers
import feedparser
from couch import db_store

@task
def fetch_feed(feedhandler, feed_urls):
    for feed_url in feed_urls:
        add_feed_items.delay(feedhandler, feed_url)

def fix_url(url):
  # Remove session key for wiley urls
  return url.split(';')[0]

@task
def add_feed_items(feedhandler, feed_url):
    """Add feed items to database.."""

    # should be smarter here, e.g. use If-Modified-Since
    feed = feedparser.parse(feed_url, agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50')

    if feedhandler in feed_handlers.handlers:
        handler = feed_handlers.handlers[feedhandler]
    else:
        handler = feed_handlers.handlers['default']

    for item in feed['items']:
        if "abstract" in handler:
            base_article = {'abstract':handler['abstract'](item)}
        else:
            base_article = {}

        item_url = fix_url(handler['url'](item))

        check_exists = db_store.view('index/sources', key=item_url, include_docs='false')

        try:
          check_exists.rows
        except:
          check_exists = db_store.view('index/sources', key=item_url, include_docs='false')

        if not check_exists.rows:
          print "Scraping", item_url
          scrape_journal.delay(item_url, base_article=base_article)
                             #handler['identifier'](item))
        else:
          print "Not scraping", item_url
