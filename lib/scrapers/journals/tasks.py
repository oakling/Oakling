import couchdb
from celery.task import task
from utils import resolve_and_scrape, merge

@task
def scrape_journal(url):
    """Find the paper in the database and then add or merge as necessary."""

    # check the store for this source url
    couch = couchdb.Server()
    db = couch['store']
    records = db.view('index/sources', key=url, include_docs='true').rows

    if not records:
        # source isn't in db
        article = resolve_and_scrape(url)
        doc_id, _ = db.save(article)
    else:
        # we've already scraped this url
        article = records[0].doc
        doc_id = article.id

    # TODO: At this stage, we check that our source doesn't have the same IDs as any other records.
      
    return doc_id

