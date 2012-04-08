from django.shortcuts import render_to_response
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
        scraping_tasks.scrape_journal.delay(bare_doc['source_url'], doc_id)
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
        
        results = itertools.chain(*[api['results'] for api in api_results])
  
        db = couchdb.Server()['store']
        docs = _add_to_store(results, db) 

        return render_to_response('search/results.html',
                                  {'api_results':api_results},
                                  context_instance=RequestContext(request))
