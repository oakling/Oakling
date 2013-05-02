import datetime
import couchdb

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView

from couch import db_store, db_journals, db_scrapers

import apps.api.views
import apps.panes.models

class HomeView(TemplateView):
    template_name = 'search/home.html'

    def get_context_data(self, **kwargs):
        # Local cache of session data
        session = self.request.session
        # Get their last visit
        last_visit = session.get('last_visit', None)
        # Update last visit
        session['last_visit'] = datetime.datetime.now()
        # Get their saved search (default to empty list)
        saved_searches = session.get('saved_searches', {})
        # Check journals in each saved search for number of recent articles
        query_objs = {}
        for query_id, search in saved_searches.items():
            article_counts = apps.api.views.articles_since(search.keys())

            query_objs[query_id] = {'count':sum(article_counts.values()),
                'queries': search}

        return {'last_visit': last_visit, 'saved_searches': query_objs}


class DocView(TemplateView):
    template_name = "doc/doc.html"

    def get_context_data(self, **kwargs):
        doc_id = self.kwargs['id']
        doc = db_store[doc_id]
        doc['docid'] = doc_id

        try:
            date_published = datetime.datetime.fromtimestamp(doc['date_published'])
        except:
            date_published = None

        # Process the IDs to make them usable in URLS
        # TODO Make this more robust, but retain slash to underscore behaviour
        pane_doc_ids = {k: v.replace('/', '_') for k, v in doc['ids'].items()}

        panes = apps.panes.models.Pane.objects.all()
        valid_panes = []
        for p in panes:
            try:
                valid_panes.append({'name': p.name,\
                    'url': p.url.format(**pane_doc_ids)})
            except KeyError:
                print "Pane not valid for article"

        return {'doc': doc, 'date_published': date_published,\
            'panes': valid_panes}


class JournalView(TemplateView):
    template_name = "search/journal.html"

    def get_context_data(self, **kwargs):
        # Get their last visit
        last_visit = self.request.session.get('last_visit')
        journal_id = self.kwargs['id']
        if not journal_id:
            # TODO Should be bad request?
            raise Http404
        try:
            journal = db_journals[journal_id]
        except couchdb.ResourceNotFound:
            # Throw a 404 if couchdb doc does not exist
            raise Http404
        return {'last_visit': last_visit, 'journal': journal}

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
  db_docs = db_store

  scrapers = [db_scrapers[doc_id] for doc_id in db_scrapers if not doc_id.startswith('_design/')]
  scrapers.append({'name': 'Default', 'module': 'akorn.scrapers.journals.scrape_meta_tags'})
  scrapers.append({'name': 'No given scraper module', 'module': None})

  for scraper in scrapers:
    scraper['num_docs'] = len(db_docs.view('rescrape/scraper', key=scraper['module'], include_docs=False).rows)
    scraper['num_rescrape'] = len(db_docs.view('rescrape/rescrape', key=scraper['module'], include_docs=False).rows)

  return render_to_response('backend/scrapers.html', {'scrapers': scrapers,}, context_instance=RequestContext(request))
