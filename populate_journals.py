import couchdb
import sys

db1 = couchdb.Server()['store']
db2 = couchdb.Server()['journals']

#for docid in db2:
#  doc = db2[docid]
#  if '_design' not in docid:
#    #print docid
#    db2.delete(doc)

for row in db1.view('index/journals', group=True).rows:
  if db2.view('index/citations', key=row.key).rows:
    print "%s already exists" % row.key
  else:
    print row.key
    journal_doc = {'citation': row.key,
                   'aliases': [row.key],}
    db2.save(journal_doc)

