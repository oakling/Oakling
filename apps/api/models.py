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

  def get_articles(self, since_time=None, since_docid=None):
    pass

  def get_num_new(self, since_time=None):
    pass

class SavedSearch:
  def get_articles(self, since_time=None, self_docid=None):
    pass

