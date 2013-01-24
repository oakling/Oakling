import json
import couchdb
import sys

db = couchdb.Server()['store']

duplicate_sources = []
i = 0

#result = db.view('dupes/duplicate_sources', group=True, reduce=True)
result = json.load(open('duplicate_sources?reduce=true&group=true'))
rows = result['rows']

i = 0
lenrows = len(rows)
for row in rows:
    if row['value'] > 1:
      #print row['key']
      source_rows = db.view('index/sources', key=row['key']).rows

      doc_ids = sorted(list(set([row2.id for row2 in source_rows])))
      if len(doc_ids) > 1:
        print doc_ids
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
