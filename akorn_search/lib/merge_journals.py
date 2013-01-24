import couchdb
import sys

server = couchdb.Server()
db = server['journals']
db_store = server['store']

def journal_article_count(journal_id):
  return len(db_store.view('index/journal_id', key=journal_id).rows)

id1 = sys.argv[1]
id2 = sys.argv[2]
dryrun = (len(sys.argv) < 4 or sys.argv[3] != 'yes')

print dryrun

count1 = journal_article_count(id1)
count2 = journal_article_count(id2)

# Merge into larger journal
#if count2 < count1:
id1, id2 = id2, id1

doc1 = db[id1]
doc2 = db[id2]

print "Merging %s into %s" % (doc2['name'], doc1['name'])

print journal_article_count(id1)
print journal_article_count(id2)

aliases = set(doc1['aliases'] + doc2['aliases'])

print aliases
print doc1['name']

if not dryrun:
  doc1['aliases'] = list(aliases)
  db.save(doc1)
  db.delete(doc2)

  print doc1

  for row in db_store.view('index/journal_id', key=id2, include_docs=True).rows:
    row.doc['journal_id_from'] = id2
    row.doc['journal_id'] = id1
    db_store.save(row.doc)

