import couchdb
from celery.task import task
from utils import scrape_and_add, link

@task
def scrape_journal(url, identifier=None):
    """Find the paper in the database and then add or merge as necessary."""

    if identifier is not None:
        # find identifier in couchdb and get the record_id
        couch = couchdb.Server()
        db = couch['store']
        records = db.view('index/ids', key=identifier, include_docs='true').rows

        if not records:
            # if identifier is not already in couchdb:
            scrape_and_add(url)
        else:
            if all(['journal' not in record.doc for record in records]):
                # there is probably no need for asychronous calls here
                new_id = scrape_and_add(url)
                link(new_id, [record.id for record in records])
    else:
        scrape_and_add(url)
