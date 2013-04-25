# Create your views here.
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
#from akorn.celery.scrapers import tasks

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
