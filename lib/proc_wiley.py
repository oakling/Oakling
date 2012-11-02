import couchdb

db = couchdb.Server()['store']

def fix_wiley_url(url):
  # http://onlinelibrary.wiley.com/doi/10.1002/adfm.201200673/abstract;jsessionid=A6D700F5F739DAF151940A60D2A20184.d02t02
  return url.split(';')[0] 

if __name__ == "__main__":
  for row in db.view('rescrape/scraper', key='lib.scrapers.journals.scrape_wiley', include_docs=True).rows:
    doc = row.doc
    print doc['source_urls']
    #doc['source_urls'] = map(fix_wiley_url, doc['source_urls'])
    #db.save(doc)

