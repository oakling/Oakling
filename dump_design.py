import couchdb
import json

db = couchdb.Server()['store']

for id in db:
  if '_design' in id:
    print json.dumps(db[id])

