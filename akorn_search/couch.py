import couchdb
import local_settings

server = couchdb.Server(local_settings.COUCH_SERVER)

def get_db(db):
  try:
    return server[db]
  except:
    return None

db_store = get_db('store')
db_journals = get_db('journals')
db_scrapers = get_db('scrapers')

