import couchdb
from couch import db_store
from celery.task import task
from utils import resolve_and_scrape, merge, ScraperNotFound, resolve_doi

def resolve_merges():
    # TODO: At this stage, we check that our source doesn't have the same IDs as any other records.
    #if article:
    #  to_merge = set()
    #
    #  for id_type, id in article['ids'].items():
    #    #print id_type, id
    #    for row in db.view('index/ids', key=id_type + ":" + id).rows:
    #      to_merge.add(row.id)
    #
    #  if len(to_merge) >= 2:
    #    pass
    pass 

@task
def rescrape_articles():
  records = db_store.view('rescrape/rescrape', include_docs='true').rows

  for record in records:
    scrape_journal.delay(record.doc['source_url'], record.doc.id)

@task
def scrape_doi(doi, doc_id=None):
    records_doi = db_store.view('index/ids', key='doi:' + doi, include_docs='true').rows

    url = resolve_doi(doi)
    records_source = db_store.view('index/sources', key=url, include_docs='true').rows
    
    if doc_id is not None or not (records_doi and records_source):
        # source url isn't in db
        if doc_id:
          article = db_store[doc_id]
          rev_id = article.rev
        else:
          article = {}
           
        try:
          scraped_article = resolve_and_scrape(url)

          # If we haven't excepted at this point, clear the current article and save it
          article.clear()
          article.update(scraped_article)

          # Add the id and revision back in since we just cleared the doc. Awkward.
          if doc_id:
            article['_id'] = doc_id
            article['_rev'] = rev_id
        except Exception, e:
          # Make a doc to remember to rescrape later
          article['error'] = str(e)
          article['rescrape'] = True
          article['source_urls'] = [url]

        if article:
          doc_id, _ = db_store.save(article)

    else:
        article = records[0].doc
        doc_id = article.id

    resolve_merges()

    return doc_id

def check_source(url):
  rows = db_store.view('index/sources', key=url, include_docs='true').rows
  
  if len(rows) == 0:
    return True
  else:
    return False

@task
def scrape_journal(url, doc_id=None, base_article={}):
    """Find the paper in the database and then add or merge as necessary."""

    # check the store for this source url
    error = None

    # Scrape if we have a doc_id or it hasn't already been scraped
    # always scrape if we're given a doc_id
    if doc_id is not None or check_source(url):
        # source url isn't in db
        if doc_id:
          article = db_store[doc_id]
          rev_id = article.rev
        else:
          article = {}
           
        try:
          scraped_article = resolve_and_scrape(url)

          # If we haven't excepted at this point, clear the current article and save it
          article.clear()
          article.update(base_article)
          article.update(scraped_article)

          # Add the id and revision back in since we just cleared the doc. Awkward.
          if doc_id:
            article['_id'] = doc_id
            article['_rev'] = rev_id
        except Exception, e:
          # Make a doc to remember to rescrape later
          article['error'] = str(type(e)) + ': ' + str(e)
          article['source_urls'] = [url]
          article['rescrape'] = True

        print article

        if article:
          # check this hasn't been inadvertantly scraped already before we go
          if check_source(article['source_urls'][-1]):
            doc_id, _ = db_store.save(article)
    else:
        # we've already scraped this url. there should only be one such doc.
        rows = db_store.view('index/sources', key=url, include_docs='true').rows
        article = rows[0].doc
        doc_id = article.id

    resolve_merges()

    return doc_id
