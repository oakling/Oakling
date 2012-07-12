from django.http import HttpResponse
from django.shortcuts import render_to_response

import datetime
import json

from django.template import RequestContext
from lib.search import citeulike, mendeley, arxiv
import Queue
import threading
import itertools
import couchdb

import lib.scrapers.journals.tasks as scraping_tasks
import lib.scrapers.journals.utils as scraping_utils

# /api/save_search?user_id=<user_id>
# /api/get_searches?user_id=<user_id>

def home(request):
    # Get their last visit
    last_visit = request.session.get('last_visit', None)
    # Update last visit
    request.session['last_visit'] = datetime.datetime.now()
    # Get their saved search (default to empty list)
    saved_searches = request.session.get('saved_searches', [])
    return render_to_response('search/home.html',
            {
                'last_visit': last_visit,
                'saved_searches': saved_searches,
            },
            context_instance=RequestContext(request))

class SearchThread(threading.Thread):
    """Threaded access to search api."""
    def __init__(self, queue, output):
        threading.Thread.__init__(self)
        self.queue = queue
        self.output = output

    def run(self):
        while True:
            api, query = self.queue.get()

            results = api['module'].search(query)

            for result in results:
              result['api'] = api
            
            self.output.append({'name':api['name'],
                                'id':api['id'],
                                'results':results})
            self.queue.task_done()

def _check_doi(doi, db):
  records = db.view('index/ids', key='doi:' + doi, include_docs=True).rows

  if len(records) == 0:
    return None
  else:
    return records[0].doc

def _check_source(source_url, db):
  records = db.view('index/sources', key=source_url, include_docs=True).rows
  
  if len(records) == 0:
    return None
  else:
    return records[0].doc

def _add_to_store(search_results, db):
  docs = []
  for result in search_results:
    # Hack for dodgy mendeley result
    if result['uri'] == 'http://www.mendeley.com/research//':
      continue
    
    bare_doc = {'title': result['title'],
                'ids': {},}
   
    bare_doc['search_api'] = result['api']['id']
 
    if 'authors' in result and result['authors'] is not None:
      bare_doc['author_names'] = result['authors']

    if 'journal' in result:
      bare_doc['journal'] = result['journal']

    if 'doi' in result and result['doi'] is not None:
      # Resolve the DOI's canonical url for the correct url.
      bare_doc['ids']['doi'] = result['doi']
      
      doc = _check_doi(result['doi'], db)
      if doc is None:
        bare_doc['source_url'] = 'http://dx.doi.org/' + result['doi']
        doc_id, _ = db.save(bare_doc)
        scraping_tasks.scrape_doi.delay(result['doi'], doc_id)

        doc = db[doc_id]
      else:
        print "%s already in db" % result['doi']
    else:
      # Check source
      doc = _check_source(result['uri'], db) 
      if doc is None:
        bare_doc['source_url'] = result['uri']
        doc_id, _ = db.save(bare_doc)
        scraping_tasks.scrape_journal.delay(result['uri'], doc_id)
        doc = db[doc_id]
      else:
        print "%s already in db" % result['uri']

    doc['api'] = result['api']
    docs.append(doc)
    
  return docs

api_weight = {'arxiv': 1.5,
              'citeulike': 1.0,
              'mendeley': 1.0,}

def score_doc(keywords, doc):
  # Function to score a doc for ordering. Pretty arbitrary.
  score = 0.0
  if 'title' in doc:
    all = True
    
    for keyword in keywords:
      if keyword in doc['title']:
        score += 0.5
      else:
        all = False

    if all:
      score *= 1.5

  if 'keyword' in doc:
    all = True
    
    for keyword in keywords:
      if keyword in doc['abstract']:
        score += 0.5
      else:
        all = False

    if all:
      score *= 1.2

  if 'author_names' in doc:
    for author_name in doc['author_names']:
      all = True
      
      for keyword in keywords:
        if type(author_name) is dict and keyword in author_name['surname'] + ' ' + author_name['forename']:
          score += 0.5
        elif keyword in author_name:
          score += 0.5
        else:
          all = False

      if all: # Bonus for all keywords being in one author's name
        score *= 2.0 

  score = score * api_weight[doc['api']['id']]

  return score

def doc_link(doc):
  if 'url' in doc['ids']:
    return doc['ids']['url']
  elif 'source_url' in doc:
    return doc['source_url']
  elif 'source_urls' in doc:
    return doc['source_urls'][len(doc['source_urls'])-1]
  elif 'doi' in doc['ids']:
    return "http://dx.doi.org/%s" % doc['ids']['doi']
  else:
    return None

def search(request):
    if 'q' in request.GET:
        queue = Queue.Queue()
        api_results = []

        apis = [ {'name':'Citeulike',
                  'id':'citeulike',
                  'module':citeulike},
                {'name':'Arxiv',
                 'id':'arxiv',
                 'module':arxiv},
                {'name':'Mendeley',
                 'id':'mendeley',
                 'module':mendeley},
                # ADSABS is too slow
                #{'name':'ADSABS',
                # 'id':'adsabs',
                # 'results':adsabs.search(request.GET['q'])},
                # Google Scholar does not like AWS
                #{'name':'Google Scholar',
                # 'id':'gscholar',
                # 'results':gscholar.search(request.GET['q'])},
               ]

        for api in apis:
            t = SearchThread(queue, api_results)
            t.setDaemon(True)
            t.start()

        for api in apis:
            queue.put((api, request.GET['q']))

        queue.join()

        keywords = request.GET['q'].split()
        
        results = itertools.chain(*[api['results'] for api in api_results])
  
        db = couchdb.Server()['store']
        docs = _add_to_store(results, db) 


        for doc in docs:
          doc['docid'] = doc['_id']
          doc['uri'] = doc_link(doc)
          doc['score'] = score_doc(keywords, doc)

        #docs = [doc for doc in docs if doc['score'] >= 1.7]

        docs = sorted(docs, key=lambda doc: doc['score'], reverse=True)

        return render_to_response('search/results.html',
                                  {'api_results':api_results,
                                   'docs':docs,
                                   'search_request': request.GET['q']},
                                  context_instance=RequestContext(request))

def doc(request, id):
  db = couchdb.Server()['store']
  doc = db[id]
  doc['docid'] = id

  date_published = datetime.datetime.fromtimestamp(doc['date_published'])

  return render_to_response('doc/doc.html',
                            {'doc': doc, 'date_published': date_published},
                            context_instance=RequestContext(request))

def journal(request, id):
  db = couchdb.Server()['store']
  # Get their last visit
  last_visit = request.session.get('last_visit', None)
  # Check the journal exists
  records = db.view('index/journals', key=id)
  if len(records.rows) == 0:
    return # Can't find journal
  
  return render_to_response('search/journal.html', {'journal': id, 'last_visit': last_visit}, context_instance=RequestContext(request))

