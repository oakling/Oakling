import couchdb
from celery.task import task
from utils import scrape_and_add, merge

@task
def scrape_journal(url, identifier=None):
    """Find the paper in the database and then add or merge as necessary."""

    if identifier is not None:
        # find identifier in couchdb and get the record_id
        couch = couchdb.Server()
        db = couch['store']
        records = db.view('index/ids', key=identifier, include_docs='true').rows

    # if identifier is already in couchdb:
        if not records:
            scrape_and_add(url)
        else:
            if 'journal' not in [record.doc['scraper'] for record in records]:
                # there is probably no need for asychronous calls here
                new_id = scrape_and_add(url)
                merge(new_id, [record.id for record in records])
    else:
        scrape_and_add(url)
