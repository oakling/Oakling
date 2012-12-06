import couchdb
import local_settings

server = couchdb.Server(local_settings.COUCH_SERVER)

db_store = server['store']
db_journals = server['journals']
db_scrapers = server['scrapers']

