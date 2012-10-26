import couchdb
import sys

db = couchdb.Server()['store']

num_done = 0
for doc_id in db:
  #print doc_id

  doc = db[doc_id]

  if 'source_urls' not in doc:
    continue

  source_url = doc['source_urls'][-1]

  row_match = db.view('index/sources', key=source_url)

  if len(row_match) != 1:
    print source_url

  if num_done % 100 == 0:
    print >>sys.stderr, num_done

  num_done += 1

