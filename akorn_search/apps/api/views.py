import time
import uuid
import re
import json
import couchdb
from datetime import datetime, date
import requests
from requests.exceptions import ConnectionError

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator

from utils import JSONResponseMixin
from apps.accounts.views import RegisterView

from couch import db_store, db_journals

class BadRequest(Exception):
    pass


class LuceneFailed(Exception):
    pass


class NoResults(Exception):
    pass


class SavedSearchMixin(object):
    def get_saved_searches(self):
        """
        Return dict of saved searches and the AkornUser object (or None)
        """
        user = self.request.user
        if user.is_authenticated():
            return user.settings, user
        else:
            return self.request.session.get('saved_searches', {}), None

    def set_saved_searches(self, saved_searches, user):
        """
        Save the saved searches against the AkornUser or against the session

        Arguments:
            saved_searches -- dict, the saved searches
            user -- AkornUser instance, the user to save against
        """
        if user:
            user.settings = saved_searches
            user.save()
        else:
            session = self.request.session
            session['saved_searches'] = saved_searches
            session.modified = True


class LoginView(View):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse(status=204)
        return HttpResponse(status=400)


class SavedSearchView(SavedSearchMixin, JSONResponseMixin, View):
    def process_query(self, query):
        """
        Return a unique ID for the query, having saved it

        Arguments:
            query -- dict, deserialised representation of the query
        """
        # Check the user has a saved search list
        searches, user = self.get_saved_searches()
        # Make an ID for this query
        query_id = str(uuid.uuid4())
        # Add the query to the saved_search dict
        searches[query_id] = query
        # Save
        self.set_saved_searches(searches, user)
        # Return the saved query's id
        return query_id

    def get(self, request, **kwargs):
        """
        Return all saved searches
        """

        searches, user = self.get_saved_searches()

        # Add code in here to add new article counts.

        return self.render_to_response(searches)

    @method_decorator(csrf_exempt)
    def post(self, request, **kwargs):
        """
        Stores searches that the user explicitly requests to be saved
        """
        query_str = request.POST.get('query')

        if not query_str:
            # Without a query to save, this is a bad request
            return HttpResponse(status=400)

        # Deserialise the give payload
        print "Saved search JSON raw", query_str
        query = json.loads(query_str)
        print "Saved search JSON loaded:", query

        # Add the given query
        query_id = self.process_query(query)

        return self.render_to_response({'query_id': query_id})


class DeleteSavedSearchView(SavedSearchMixin, View):
    def get(self, request, *args, **kwargs):
        """
        Removes a users stored search
        """
        query_id = request.GET.get('query_id')
        if not query_id:
            # Without a query this is a bad request
            return HttpResponse(status=400)
        # Get the list of searches
        saved_searches, user = self.get_saved_searches()
        # If there are no saved searches yet
        if not saved_searches:
            return HttpResponse(status=404)
        try:
            # Rip out the query if it exists
            del saved_searches[query_id]
            # Save the modified saved_searches dict
            self.set_saved_searches(saved_searches, user)
        except KeyError:
            # If item does not exist then it is a bad request
            return HttpResponse(status=400)
        # Success but no content
        return HttpResponse(status=204)

class LuceneRequest(object):
    lucene_url = settings.LUCENE_URL
    max_limit = 50
    delimiter = '|'

    @staticmethod
    def lucene_process(response):
        return [x['doc'] for x in response.get('rows', [])]

    @classmethod
    def lucene_split_keywords(cls, arg):
        try:
            arg = arg.strip()
            if not arg:
                return []
            args = arg.split(cls.delimiter)
            return [_.split(' ') for _ in args]
        except AttributeError:
            return []

    @classmethod
    def lucene_split_arg(cls, arg):
        try:
            arg = arg.strip()
            if not arg:
                return []
            return arg.split(cls.delimiter)
        except AttributeError:
            return []

    def lucene_request(self, query, doc_limit, doc_skip):
        options = {
            'q': query,
            'include_docs': 'true',
            'stale': 'ok',
            'limit': doc_limit,
            'sort': '\sort_date'
            }

        # Check if a number of articles to skip has been specified
        if doc_skip:
            options['skip'] = doc_skip

        response = requests.get(self.lucene_url, params=options)

        if response.status_code == 404:
            raise ConnectionError('Lucene not found')

        return response.json()

    @staticmethod
    def lucene_get_query(keywords=[], journals=[], since=None):
        # It is badness to not search for anything
        if not keywords and not journals:
            raise BadRequest()

        parts = []

        if keywords:
            # AND between all keywords
            # The last word may not be complete - add a wildcard character
            keywords_str = "(" + " OR ".join(['(' + ' AND '.join(_) + ')' for _ in keywords]) + ")"

            parts.append(keywords_str)

        # Deal with the case that there are no journals to be filtered by
        if journals:
            journals_str = 'journalID:({})'.format(' OR '.join(journals))
            
            parts.append(journals_str)

        # Add timestamp lower bound if present
        if since is not None:
            since_str = 'sort_date:[{} TO *]'.format(since)
            
            parts.append(since_str)
          
        return ' AND '.join(parts)

class ArticlesView(LuceneRequest, TemplateView):
    """
    Takes a search query and responds with a list of articles as HTML
    """
    template_name = 'search/article_list.html'

    def lucene_search(self):
        # Get keywords from request parameters
        keywords = self.lucene_split_keywords(self.request.GET.get('k'))

        # Get journals from request parameters
        journals = self.lucene_split_arg(self.request.GET.get('j'))

        # Construct the lucene query
        query = self.lucene_get_query(keywords, journals)
        resp = self.lucene_request(query, self.doc_limit, self.doc_skip)

        return self.lucene_process(resp)

    @property
    def doc_limit(self):
        try:
            return int(self.request.GET.get('limit', self.max_limit))
        except ValueError:
            raise BadRequest('Invalid value supplied for limit')

    @property
    def doc_skip(self):
        try:
            return int(self.request.GET.get('skip'))
        except TypeError:
            return None
        except ValueError:
            raise BadRequest('Invalid value supplied for skip')

    def process_docs(self, lucene_docs):
        for d in lucene_docs:
            # Cannot use _id inside a Django template
            d['docid'] = d['_id']
            # Convert unix timestamp to date object
            d['date'] = self.get_doc_date(d)
        return lucene_docs

    @staticmethod
    def get_doc_date(doc):
        """
        Select the most relevant date from the ones available
        """
        timestamp = doc.get('date_scraped')
        if timestamp:
            # Process the timestamp to produce a datetime
            return datetime.fromtimestamp(timestamp)
        return None

    def get_context_data(self, **kwargs):
        """
        Return the context to the template
        """
        docs = self.process_docs(self.lucene_search())
        if not docs:
            raise NoResults()
        # Create the context structure
        context = {'docs': docs}
        return context

    def get(self, *args, **kwargs):
        """
        Returns the appropriate HttpResponse
        """
        try:
            return super(ArticlesView, self).get(*args, **kwargs)
        except NoResults as e:
            return HttpResponse(e.message, status=204)
        except BadRequest as e:
            return HttpResponse(e.message, status=400)
        except LuceneFailed as e:
            return HttpResponse(e.message, status=503)

class ArticlesViewXML(ArticlesView):
    template_name = 'search/article_list.xml'

class JournalAutoCompleteView(JSONResponseMixin, View):
    @classmethod
    def get_journal_docs(cls, db=None):
        cache_key = 'journals'
        cached = cache.get(cache_key)

        if cached:
            print "cache size", len(cached)
            return json.loads(cached)

        # If it is not cached then work it out
        db = db_journals
        journal_docs = list([db[doc_id] for doc_id in db])

        for doc in journal_docs:
            doc['id'] = doc.id
            if 'aliases' in doc:
                doc['sorted_aliases'] = sorted([(cls.clean_journal(alias), alias) for alias in doc['aliases']], key=lambda a: len(a), reverse=True)
            else:
                doc['sorted_aliases'] = []

        # Set the cache, expiring after 1 day
        cache.set(cache_key, json.dumps(journal_docs), 86400)
	
	print "to cache size", len(json.dumps(journal_docs))

        return journal_docs

    @staticmethod
    def clean_journal(s):
        # keep only alphanumeric characters for comparison purposes
        try:
            return re.sub('\s+', ' ', re.sub('[^a-z]', ' ', s.lower()))
        except:
            return None

    @classmethod
    def find_journals(cls, query):
        # Set up empty list to store what we want to return
        journals = []
        # Note that get_journal_docs is an expensive call
        for doc in cls.get_journal_docs():
            try:
                for alias in doc['sorted_aliases']:
                    if query and query in alias[0]:
                        journals.append({'full': doc['name'], 'text': alias[1], 'id': doc['id'], 'type': 'journal'})
                        break
                    elif not query:
                        journals.append({'full': doc['name'], 'text': alias[1], 'id': doc['id'], 'type': 'journal'})
                        break
            except KeyError:
                # If the journal has no name, skip it
                continue
        return journals

    def get(self, request, *args, **kwargs):
        # Get string to look for
        query = self.clean_journal(request.GET.get('term'))
        found = self.find_journals(query)
        return self.render_to_response(found)

def articles_since(journals, timestamp=None):
    """
    Returns a dict of journal IDs and article counts
    Takes a list of journal IDs and a timestamp to count from
    """
    db = db_store
    output = {}

    #if timestamp is not None:
    timestamp = time.mktime(date.today().timetuple())

    # TODO Do this with one couch query?
    for journal_id in journals:
        rows = db.view('articles/latest_journal',
            include_docs=False,
            startkey=[journal_id, timestamp],
            endkey=[journal_id, {}],
            descending=False)
        output[journal_id] = len(rows)

    return output

class ArticleCountView(JSONResponseMixin, View, LuceneRequest):
    doc_limit = 100
    doc_skip = 0

    def lucene_search(self):
        # Get keywords from request parameters
        keywords = self.lucene_split_keywords(self.request.GET.get('k'))

        # Get journals from request parameters
        journals = self.lucene_split_arg(self.request.GET.get('j'))

        timestamp = int(self.request.GET.get('time'))

        # Construct the lucene query
        query = self.lucene_get_query(keywords, journals, timestamp)
        resp = self.lucene_request(query, self.doc_limit, self.doc_skip)

        return resp #self.lucene_process(resp)

    def get(self, *args, **kwargs):
        """
        Returns as JSON a dict of journal IDs and article counts
        Takes a + separated string of journal IDs and a UNIX timestamp in s:
        If no timestamp is provided it gives count of articles published today
        """

        return HttpResponse(self.lucene_search()['total_rows'])

    #def post(self, *args, **kwargs):
    #    """
    #    Returns as JSON a dict of journal IDs and article counts
    #    Takes a JSON serialize query object and a UNIX timestamp in s
    #    """
    #    query = self.request.POST.get('q')
    #    time_s = self.request.POST.get('time')
    #    if not query:
    #        return HttpResponse(status=400)
    #    return self.articles_since(json.loads(query.keys()), time_s)


class JSONRegisterView(JSONResponseMixin, RegisterView):
    def post(self, request, *args, **kwargs):
	form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = {}
        status = 200
        if form.is_valid():
		self.create_user(form)
	else:
            context['errors'] = form.errors
            status = 400
        return self.render_to_response(context, status=status)
