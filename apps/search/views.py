from django.http import HttpResponse
from django.shortcuts import render_to_response

import json

from django.template import RequestContext
from lib.search import citeulike, mendeley, arxiv
import Queue
import threading
import itertools
import couchdb

import lib.scrapers.journals.tasks as scraping_tasks
import lib.scrapers.journals.utils as scraping_utils

def home(request):
    return render_to_response('search/home.html',
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
    bare_doc = {'title': result['title'],
                'author_names': result['authors'],
                'ids': {},}

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
        docs.append(db[doc_id])
      else:
        print "%s already in db" % result['doi']
        docs.append(doc)
    else:
      # Check source
      doc = _check_source(result['uri'], db) 
      if doc is None:
        bare_doc['source_url'] = result['uri']
        doc_id, _ = db.save(bare_doc)
        scraping_tasks.scrape_journal.delay(result['uri'], doc_id)
        docs.append(db[doc_id])
      else:
        print "%s already in db" % result['uri']
        docs.append(doc)

  return docs

def score_doc(keywords, doc):
  # Function to score a doc for ordering. Pretty arbitrary.
  score = 0.0
  for keyword in keywords:
    if 'title' in doc and keyword in doc['title']:
      score += 0.5
    if 'keyword' in doc and keyword in doc['abstract']:
      score += 0.5
    if 'author_names' in doc:
      for author_name in doc['author_names']:
        if type(author_name) is dict:
          if keyword in author_name['surname'] + ' ' + author_name['forename']:
            score += 0.5
        elif keyword in author_name:
          score += 0.5
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

        docs = sorted(docs, key=lambda doc: score_doc(keywords, doc), reverse=True)

        for doc in docs:
          doc['docid'] = doc['_id']
          doc['uri'] = doc_link(doc)
          print doc['title'], score_doc(keywords, doc)

        return render_to_response('search/results.html',
                                  {'api_results':api_results,
                                   'docs':docs,
                                   'search_request': request.GET['q']},
                                  context_instance=RequestContext(request))

def doc(request, id):
  db = couchdb.Server()['store']
  doc = db[id]

  return render_to_response('doc/doc.html',
                            {'doc': doc,},
                            context_instance=RequestContext(request))
  
