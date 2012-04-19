import json
import sys
import couchdb

db = couchdb.Server()['store']

docs = json.load(open(sys.argv[1]))

for doc in docs:
	if doc['_id'] in db:
		doc_old = db[doc['_id']]
		rev_id = doc_old.rev
		doc['_rev'] = rev_id
	db.save(doc)
