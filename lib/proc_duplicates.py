import couchdb
import sys

db = couchdb.Server()['store']

f = open('duplicates.txt')

duplicates = set()

for duplicate_id in f:
  duplicate_id = duplicate_id.strip()

  duplicates.add(duplicate_id)

print >>sys.stderr, len(duplicates), "duplicated ids"

dupes = set()

for duplicate_id in duplicates:
  duplicate_docs = db.view('index/ids', key=duplicate_id, include_docs=True)

  print >>sys.stderr, duplicate_id
  same_source = {}
  for doc in duplicate_docs[1:]:
    final_source = doc.doc['source_urls'][-1]
    
    if final_source in same_source:
      same_source[final_source].add(doc.id)
    else:
      same_source[final_source] = set([doc.id])

    for key, ids in same_source.items():
      for doc_id in list(ids)[1:]:
        dupes.add(doc.id)

for doc_id in dupes:
  print doc_id

