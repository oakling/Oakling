import couchdb

db = couchdb.Server()['store']

for id in db:
  if '_design' in id:
    continue
  else:
    print db[id]['title']
    db.delete(db[id])

