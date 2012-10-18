from django.db import models
import couchdb

db_store = couchdb.Server()['store']
db_journals = couchdb.Server()['journals']

class Article:
  pass

class Journal:
  def __init__(self, doc):
    self.doc = doc

  @classmethod
  def get_journal(klass, journal_id):
    doc = db_journals[journal_id]
    return Journal(doc)

  def get_num_new(self, since_time=None):
    rows = db.view('articles/latest_journal',
            include_docs=True,
            startkey=[self.doc._id, since_time],
            endkey=[self.doc._id, {}],
            descending=False)

    return len(rows)

class SavedSearch:
  def get_articles(self, since_time=None, self_docid=None):
    pass

if False:
  def get_articles_all(self, num=20, since_time=None, since_docid=None):
    if 'all' in last_ids:
      all_rows = list(db.view('articles/latest', limit=num,
                              include_docs=True, startkey=since_time,
                              startkey_docid=since_docid, skip=1, descending=True))
    else:
      all_rows = list(db.view('articles/latest', limit=num,
                              include_docs=True, descending=True))

    last_ids_json = json.dumps({'all': (all_rows[-1].key, all_rows[-1].doc['_id'])})
    
    all_rows = sorted(all_rows, key=lambda row: row.doc['date_published'], reverse=True)

    return all_rows

  def get_articles_filter(self, journals=[], num=20, since_time={}, since_docid={}):
    all_rows = []
    for journal in journals:
      if journal in last_ids:
        rows = db.view('articles/latest_journal', limit=num, include_docs=True,
                       startkey=since_time[journal], startkey_docid=since_docid[journal],
                       endkey=[journal], skip=1, descending=True)
      else:
        rows = db.view('articles/latest_journal', limit=num, include_docs=True,
                       endkey=[journal], startkey=[journal,{}], descending=True)

      rows_journal = rows.rows
      all_rows += rows_journal

    all_rows = sorted(all_rows, key=lambda row: row.doc['date_published'], reverse=True)[:num]

    return all_rows
