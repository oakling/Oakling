import couchdb
import json

db = couchdb.Server()['store']

docs = []
for id in db:
  if '_design' in id:
    doc = db[id]
    del doc['_rev']
    docs.append(doc)

print json.dumps(docs)
