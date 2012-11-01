import couchdb
import sys

db1 = couchdb.Server()['store']
db2 = couchdb.Server()['journals']

missing_journals = set()

for row in db1.view('errors/nojournalid', include_docs=True).rows:
  doc = row.doc
  #print doc

  if 'rescrape' in doc and doc['rescrape']:
    continue

  if 'journal' in doc:
    journal_name = doc['journal']
  elif 'citation' in doc and 'journal' in doc['citation']:
    journal_name = doc['citation']['journal']
  elif 'categories' in doc and 'arxiv' in doc['categories']:
    journal_name = 'arxiv:' + doc['categories']['arxiv'][0]
  else:
    continue

  if journal_name is not None:
    missing_journals.add(journal_name)

for missing_journal in missing_journals:
  print missing_journal

  journal_doc = {'name': missing_journal,
                 'aliases': [missing_journal,],}

  db2.save(journal_doc)

