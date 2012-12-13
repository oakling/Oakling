import couchdb
import json
from couch import db_store as db

docs = []
for id in db:
  if '_design' in id:
    doc = db[id]
    del doc['_rev']
    docs.append(doc)

print json.dumps(docs)
