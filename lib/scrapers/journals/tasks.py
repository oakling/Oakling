import couchdb
from celery.task import task
from utils import resolve_and_scrape, merge, ScraperNotFound

@task
def rescrape_articles():
  db = couchdb.Server()['store']

  records = db.view('rescrape/rescrape', include_docs='true').rows

  for record in records:
    scrape_journal.delay(record.doc['source_url'], record.doc.id)

@task
def scrape_journal(url, doc_id=None):
    """Find the paper in the database and then add or merge as necessary."""

    # check the store for this source url
    server = couchdb.Server()

    db = server['store']

    records = db.view('index/sources', key=url, include_docs='true').rows

    error = None

    print doc_id
    if doc_id is not None or not records:
        # source url isn't in db
        if doc_id:
          article = db[doc_id]
          rev_id = article.rev
        else:
          article = {}
           
        try:
          print "Scraping", url
          scraped_article = resolve_and_scrape(url)

          # If we haven't excepted at this point, clear the current article and save it
          article.clear()
          article.update(scraped_article)

          if doc_id:
            article['_id'] = doc_id
            article['_rev'] = rev_id
        except Exception, e:
          # Make a doc to remember to rescrape later
          article['error'] = str(e)
          article['source_url'] = url
          article['rescrape'] = True

        if article:
          doc_id, _ = db.save(article)
    else:
        # we've already scraped this url. there should only be one such doc.
        article = records[0].doc
        doc_id = article.id

    # TODO: At this stage, we check that our source doesn't have the same IDs as any other records.
    if article:
      to_merge = set()

      for id_type, id in article['ids'].items():
        #print id_type, id
        for row in db.view('index/ids', key=id_type + ":" + id).rows:
          to_merge.add(row.id)

      if len(to_merge) >= 2:
        pass

    return doc_id
