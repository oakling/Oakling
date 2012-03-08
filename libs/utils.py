import couchdb

def save(doc):
    db = couchdb.Server()['store']
    doc_id, doc_rev =  db.save(doc)
    return doc_id
