import datetime
import couchdb

from django.http import Http404
from django.views.generic import TemplateView

from couch import db_store, db_journals

import apps.api.views
import apps.panes.models

class HomeView(TemplateView):
    template_name = 'search/home.html'


class DocView(TemplateView):
    template_name = "search/doc.html"

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
        pane_doc_ids = {k: v.replace('/', '_') for k, v in doc['ids'].iteritems()}

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
