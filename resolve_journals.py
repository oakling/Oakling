import couchdb

server = couchdb.Server()
db_store = server['store']
db_journals = server['journals']

count = 0

for doc_id in db_store:
  doc = db_store[doc_id]

  if 'journal' in doc:
    journal_name = db_store[doc_id]['journal']
  elif 'citation' in doc and 'journal' in doc['citation']['journal']:
    journal_name = db_store[doc_id]['citation']['journal']
  elif 'categories' in doc and 'arxiv' in doc['categories']:
    journal_name = 'arxiv:' + db_store[doc_id]['categories']['arxiv'][0]
  else:
    continue

  matches = db_journals.view('index/aliases', key=journal_name).rows

  if matches:
    match = matches[0]
    doc['journal_id'] = match.id
    db_store.save(doc)

  if count % 100 == 0:
    print count

  count += 1
  #  print journal_name, match.id #doc['journal_id']
  #else:
  #  print "X", journal_name
