import lib.scrapers.journals.tasks
import sys
import couchdb
import couch

if len(sys.argv) == 2:
  db = couch.store

  rows = db.view('rescrape/rescrape', key=sys.argv[1], include_docs=True).rows

  print len(rows)

  for row in rows:
    #print row.doc['title']
    #row.doc['rescrape'] = True
    #db.save(row.doc)
    
    #if 'rescrape' not in row.doc or not row.doc['rescrape']:
    #  continue

    print row.doc.id

    #lib.scrapers.journals.tasks.scrape_journal.delay(row.doc['source_url'], row.doc.id)
    if 'source_url' in row.doc:
      lib.scrapers.journals.tasks.scrape_journal.delay(row.doc['source_url'], row.doc.id)
    if 'source_urls' in row.doc:
      lib.scrapers.journals.tasks.scrape_journal.delay(row.doc['source_urls'][0], row.doc.id)
    elif 'scraper_source' in row.doc:
      lib.scrapers.journals.tasks.scrape_journal.delay(row.doc['scraper_source'], row.doc.id)
else:
  lib.scrapers.journals.tasks.rescrape_articles()

