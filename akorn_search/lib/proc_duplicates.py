import couchdb
import sys

db = couchdb.Server()['store']

f = open('duplicates_sources.txt')

duplicates = set()

for duplicate_source in f:
  duplicate_source = duplicate_source.strip()

  duplicates.add(duplicate_source)

print >>sys.stderr, len(duplicates), "duplicated sources"

dupes = set()

for duplicate_source in duplicates:
  duplicate_docs = db.view('index/sources', key=duplicate_source, include_docs=True).rows

  print >>sys.stderr, duplicate_source

  for row in duplicate_docs[1:]:
    db.delete(row.doc)

