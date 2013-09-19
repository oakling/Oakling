import json
import couchdb
import sys
from celery.couch import db_store as db

duplicate_sources = []
i = 0

result = json.load(open('data_dumps/duplicate_doi_scraper?reduce=true&group=true'))
rows = result['rows']

i = 0
lenrows = len(rows)

for row in rows:
    if row['key'][0] == "akorn.scrapers.journals.scrape_wiley" and row['key'][1] != None and row['value'] > 1:
      source_rows = db.view('index/ids', key="doi:" + row['key'][1]).rows

      doc_ids = sorted(list(set([row2.id for row2 in source_rows])))
      if len(doc_ids) > 1:
        for doc_id in doc_ids[1:]:
          doc = db[doc_id]
          db.delete(doc)

    if i % 100 == 0:
      print i, lenrows

    i += 1

#print len(duplicate_sources), "duplicates"

#for source in duplicate_sources:
#  rows = db.view('index/sources', key=source).rows
#
#  doc_ids = sorted(list(set([row.id for row in rows])))

#  if len(doc_ids) > 1:
#    print doc_ids
    #for doc_id in doc_ids[1:]:
    #  doc = db[doc_id]
    #  db.delete(doc)
