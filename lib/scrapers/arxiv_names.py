import urllib2
import couchdb
import lxml.html

db = couchdb.Server()['journals']

for doc_id in db:
  doc = db[doc_id]
 
  if '_design' in doc.id:
    continue
 
  if 'citation' in doc:
    doc['name'] = doc['citation']
    del doc['citation']
    db.save(doc)

  if 'arxiv:' not in doc['name']:
    continue

  arxiv_category = doc['name'][len('arxiv:'):]
  url = "http://arxiv.org/list/%s/recent" % arxiv_category

  page = urllib2.urlopen(url).read()
  tree = lxml.html.fromstring(page)

  title = tree.xpath('//h1')[1].text_content().strip()

  doc['name'] = "%s (%s)" % (title, arxiv_category)
  doc['aliases'].append(doc['name'])

  db.save(doc)

  print doc['name']
