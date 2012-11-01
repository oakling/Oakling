import couchdb

server = couchdb.Server()
db_store = server['store']
db_journals = server['journals']

count = 0

cache = {}

rows = db_store.view('errors/nojournalid', include_docs=True).rows

print "%d docs to match journal id for" % len(rows)

for row in rows:
  doc = row.doc

  if 'journal_id' in doc:
    continue

  if 'citation' in doc and 'journal' in doc['citation']:
    journal_name = doc['citation']['journal']
  elif 'journal' in doc:
    journal_name = doc['journal']
  elif 'categories' in doc and 'arxiv' in doc['categories']:
    journal_name = 'arxiv:' + doc['categories']['arxiv'][0]
  else:
    continue

  if journal_name in cache:
    journal_id = cache[journal_name]
  else:
    matches = db_journals.view('index/aliases', key=journal_name).rows

    if matches:
      journal_id = matches[0].id
      cache[journal_name] = journal_id
    else:
      journal_id = None

  if journal_id:
    doc['journal_id'] = journal_id
    db_store.save(doc)
    pass
    #print journal_name, journal_id
  else:
    print "Can't find", journal_name

  if count % 100 == 0:
    print count

  count += 1
  #  print journal_name, match.id #doc['journal_id']
  #else:
  #  print "X", journal_name
