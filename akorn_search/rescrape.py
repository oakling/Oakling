import sys
import couchdb
import couch

from akorn.celery.scrapers import tasks

if True or len(sys.argv) == 2:
  db = couch.db_store

#  rows = db.view('rescrape/rescrape', key=sys.argv[1], include_docs=True).rows
  rows = db.view('rescrape/rescrape', include_docs=True).rows

  print len(rows)

  for ind, row in enumerate(rows):
    #print row.doc['title']
    #row.doc['rescrape'] = True
    #db.save(row.doc)
    
    #if 'rescrape' not in row.doc or not row.doc['rescrape']:
    #  continue

    print "%d: "%ind + str(row.doc.id)

    #lib.scrapers.journals.tasks.scrape_journal.delay(row.doc['source_url'], row.doc.id)
    try:
      if 'source_url' in row.doc:
        print row.doc['source_url']
        tasks.scrape_journal(row.doc['source_url'], row.doc.id)
      if 'source_urls' in row.doc:
        print row.doc['source_urls']
        tasks.scrape_journal(row.doc['source_urls'][0], row.doc.id)
      elif 'scraper_source' in row.doc:
        print row.doc['scraper_source']
        tasks.scrape_journal(row.doc['scraper_source'], row.doc.id)
    except Exception, e:
      print "eep! -- " + str(type(e)) + ': ' + str(e)
else:
  tasks.rescrape_articles()

