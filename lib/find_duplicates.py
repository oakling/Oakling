import couchdb
import sys

db = couchdb.Server()['store']

duplicate_sources = []
for row in db.view('dupes/duplicate_sources', group=True).rows:
  if row.value > 1:
    duplicate_sources.append(row.key)

print len(duplicate_sources), "duplicates"

for source in duplicate_sources:
  rows = db.view('index/sources', key=source).rows

  doc_ids = sorted(list(set([row.id for row in rows])))

  if len(doc_ids) > 1:
    print doc_ids
    #for doc_id in doc_ids[1:]:
    #  doc = db[doc_id]
    #  db.delete(doc)
