from django.http import HttpResponse
from django.shortcuts import render_to_response

import datetime, time
import json

from django.template import RequestContext
from lib.search import citeulike, mendeley, arxiv
import Queue
import threading
import itertools
import couchdb

from couch import db_store, db_journals, db_scrapers
from akorn.celery.scrapers import tasks

#import lib.scrapers.journals.tasks as scraping_tasks
#import lib.scrapers.journals.utils as scraping_utils
import apps.api.views

from apps.panes.models import Pane

# /api/save_search?user_id=<user_id>
# /api/get_searches?user_id=<user_id>

def home(request):
    # Get their last visit
    last_visit = request.session.get('last_visit', None)
    # Update last visit
    request.session['last_visit'] = datetime.datetime.now()
    # Get their saved search (default to empty list)
    saved_searches = request.session.get('saved_searches', {})
    # Check journals in each saved search for number of recent articles
    query_objs = {}
    for query_id, search in saved_searches.items():
        article_counts = apps.api.views.articles_since(search.keys())
           #time.mktime(last_visit.timetuple()))

        query_objs[query_id] = {'count':sum(article_counts.values()),
            'queries': search}

    return render_to_response('search/home.html',
            {
                'last_visit': last_visit,
                'saved_searches': query_objs,
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
        #scraping_tasks.scrape_doi.delay(result['doi'], doc_id)

        doc = db[doc_id]
      else:
        print "%s already in db" % result['doi']
    else:
      # Check source
      doc = _check_source(result['uri'], db) 
      if doc is None:
        bare_doc['source_url'] = result['uri']
        doc_id, _ = db.save(bare_doc)
        #scraping_tasks.scrape_journal.delay(result['uri'], doc_id)
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
  
        db = db_store 
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
  db = db_store 
  doc = db[id]
  doc['docid'] = id
  try:
    date_published = datetime.datetime.fromtimestamp(doc['date_published'])
  except:
    date_published = None

  # Process the IDs to make them usable in URLS
  # TODO Make this more robust, but retain slash to underscore behaviour
  pane_doc_ids = {k: v.replace('/', '_') for k, v in doc['ids'].items()}

  panes = Pane.objects.all()
  valid_panes = []
  for p in panes:
    try:
      valid_panes.append({'name': p.name, 'url': p.url.format(**pane_doc_ids)})
    except KeyError:
      print "Pane not valid for article"
  return render_to_response('doc/doc.html', {'doc': doc, 'date_published': date_published, 'panes': valid_panes}, context_instance=RequestContext(request))

def journal(request, id):
  # Get their last visit
  last_visit = request.session.get('last_visit', None)

  db = db_journals 

  # Check the journal exists
  if id not in db:
    return
  else:
    journal_doc = db[id]

  return render_to_response('search/journal.html', {'last_visit': last_visit, 'journal': journal_doc,}, context_instance=RequestContext(request))

def backend_journals(request):
  db_docs = db_store
  
  journals = [db_journals[doc_id] for doc_id in db_journals if '_design' not in doc_id]

  journals = sorted(journals, key=lambda doc: doc['name'])

  for journal in journals:
    journal.num_docs = len(db_docs.view('index/journal_id', key=journal.id, include_docs=False).rows)

  return render_to_response('backend/journals.html', {'journals': journals,}, context_instance=RequestContext(request))

def backend_journal(request, journal_id):
  db_docs = db_store 
  journal_doc = db_journals[journal_id]

  rows = db_docs.view('index/journal_id', key=journal_id, include_docs=True).rows

  num_rescrape = 0
  scraper_modules = set()
  
  docs = [row.doc for row in rows]

  for row in rows:
    doc = row.doc
    if 'rescrape' in doc and doc['rescrape']:
      num_rescrape += 1
   
    if 'scraper_module' in doc:
      scraper_modules.add(doc['scraper_module'])

  return render_to_response('backend/journal.html', {'journal': journal_doc,
                                                     'docs': docs,
                                                     'num_rescrape': num_rescrape,
                                                     'scraper_modules': list(scraper_modules),},
                            context_instance=RequestContext(request))

def backend_scrapers(request):
    scrapers = {}

    scrapers['Unable to resolve'] = {'name': 'Scraper Unresolved', 
                                     'module': None, 
                                     'num_docs': 0,
                                     'error_type_count': 0,
                                     'errors': []}
    scrapers['Scraper Module Missing'] = {'name': 'Scraper Module Missing', 
                                          'module': None, 
                                          'num_docs': 0,
                                          'error_type_count': 0,
                                          'errors': []}

    for row in db_store.view('rescrape/scraper_exception_error_count', group=True).rows:
        module, error = row['key']
        scrapers.setdefault(module, 
                            { 'name': module.split('.')[-1],
                              'module': module,
                              'num_docs': 0,
                              'error_type_count': 0,
                              'errors': []})
        scrapers[module]['error_type_count'] += 1
        scrapers[module]['errors'].append({ 'exception': error,
                                       'num_rescrape': row['value'] })

    for row in db_store.view('rescrape/scraper_total_docs', group=True):
        module = row['key']
        if module in scrapers:
            scrapers[module]['num_docs'] = row['value']

    scrapers = scrapers.values()

    return render_to_response( 'backend/scrapers.html', 
                               {'scrapers': scrapers,}, 
                               context_instance=RequestContext(request) )

def backend_scraper_detail(request, scraper_module):
    exceptions = {}
    for row in db_store.view('rescrape/rescrape', key=scraper_module, include_docs=True).rows:
        doc = row.doc
        exceptions.setdefault(doc['exception'], 
                          {'exception': doc['exception'],
                           'num_errors': 0,
                           'errors': [],})
        exceptions[doc['exception']]['num_errors'] += 1
        exceptions[doc['exception']]['errors'].append(
            { 'error_text': doc['error_text'],
              'source_urls': doc['source_urls'], 
              'doc_id': doc.id})

    exceptions = exceptions.values()

    return render_to_response( 'backend/scraper_detail.html',
                               {'scraper_module': scraper_module,
                                'exceptions': exceptions,
                               },
                               context_instance=RequestContext(request) )

# Yuck... mixing view and behaviour...
# Which module should contain rescrape_doc?  
# Similarly, am I calling it in a sane way?
def rescrape_doc(doc):
    try:
        if 'source_url' in doc:
            print doc['source_url']
            tasks.scrape_journal(doc['source_url'], doc.id)
        if 'source_urls' in doc:
            print doc['source_urls']
            tasks.scrape_journal(doc['source_urls'][0], doc.id)
        elif 'scraper_source' in doc:
            print doc['scraper_source']
            tasks.scrape_journal(doc['scraper_source'], doc.id)
    except Exception, e:
        print "eep! -- " + str(type(e)) + ': ' + str(e)

def backend_rescrape(request):
    if request.method == "POST":
        print request.POST
        if request.POST['source'] == 'main':
            print "MAIN"
            num_to_rescrape = 0
            for row in db_store.view(
                'rescrape/scraper_exception_errors', 
                key=(request.POST['scraper_module'], request.POST['exception']), 
                include_docs=True ).rows:
                rescrape_doc(row.doc)
                num_to_rescrape += 1
        elif request.POST['source'] == 'details':
            print "DETAILS"
            rescrape_doc(db_store[request.POST['doc_id']])
            num_to_rescrape = 1

        return render_to_response( 'backend/rescrape.html',
                                   {'num_to_rescrape': str(num_to_rescrape)},
                                   context_instance=RequestContext(request) )
    else:
        return render_to_response( 'backend/rescrape.html',
                                   {'num_to_rescrape': "none"},
                                   context_instance=RequestContext(request) )
