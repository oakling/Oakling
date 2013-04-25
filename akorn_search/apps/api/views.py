import time
import uuid
import re
import json
import Queue
import threading
import itertools
import couchdb
import datetime
import string
import requests

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView


from lib.search import citeulike, mendeley, arxiv

from couch import db_store, db_journals

class BadRequest(Exception):
    pass


def get_journal_docs(db=None):
  db = db_journals

  journal_docs = list([db[doc_id] for doc_id in db])

  for doc in journal_docs:
    if 'aliases' in doc:
      doc['sorted_aliases'] = sorted([(clean_journal(alias), alias) for alias in doc['aliases']], key=lambda a: len(a), reverse=True)
    else:
      doc['sorted_aliases'] = []

  return journal_docs

def clean_journal(s):
  # keep only alphanumeric characters for comparison purposes
  try:
    return re.sub('\s+', ' ', re.sub('[^a-z]', ' ', s.lower()))
  except:
    return None

journal_doc_cache = get_journal_docs()

@csrf_exempt
def save_search(request):
    """
    Stores searches that the user explicitly requests to be saved
    """
    query_str = request.POST.get('query')

    if not query_str:
        # Without a query to save, this is a bad request
        return HttpResponse(status=400)

    query = json.loads(query_str)

    saved_searches = request.session.get('saved_searches', None)
    # Check the user has a saved search list
    if not saved_searches:
        # Make an empty list
        request.session['saved_searches'] = {}
    # Make an ID for this query
    query_id = str(uuid.uuid4())
    # Add the query to the users saved_search list
    request.session['saved_searches'][query_id] = query
    # Make sure sessions is saved
    request.session.modified = True
    # Success, and return the saved query's id
    return HttpResponse(json.dumps({'query_id': query_id}), mimetype="application/json", status=200)

def del_saved_search(request):
    """
    Removes a users stored search
    """
    query_id = request.GET.get('query_id')
    if not query_id:
        # Without a query this is a bad request
        return HttpResponse(status=400)
    # Get the list of searches
    saved_searches = request.session.get('saved_searches')
    if not saved_searches:
        return HttpResponse(status=404)
    # Rip out the query if it exists
    try:
        del request.session['saved_searches'][query_id]
        # Raises a KeyError if item does not exist
    except KeyError:
        return HttpResponse(status=400)
    # Make sure session is saved
    request.session.modified = True
    # Success but no content
    return HttpResponse(status=204)


class ArticlesView(TemplateView):
    """
    Takes a search query and responds with a list of articles as HTML
    """
    template_name = 'search/article_list.html'
    lucene_url = settings.LUCENE_URL
    max_limit = 50

    def lucene_request(self, query, skip=None):
        options = {
            'q': query,
            'include_docs': 'true',
            'stale': 'ok',
            'sort': '\sort_date',
            }
        # Check if a limit has been specified
        limit = int(self.request.GET.get('limit'))
        if limit and limit < self.max_limit:
            options['limit'] = limit
        else:
            options['limit'] = self.max_limit
        # Check if a number of articles to skip has been specified
        skip = self.request.GET.get('skip')
        if skip:
            options['skip'] = int(skip)
        return requests.get(self.lucene_url, params=options).json()

    def lucene_process(self, response):
        return [x['doc'] for x in response['rows']]

    def lucene_split_keywords(self, arg):
        try:
            arg = arg.strip()
            if not arg:
                return []
            args = arg.split(' ')
            arg_blocks = [a.split('+') for a in args]
            return arg_blocks
        except AttributeError:
            return []

    def lucene_split_arg(self, arg):
        try:
            arg = arg.strip()
            if not arg:
                return []
            return arg.split('+')
        except AttributeError:
            return []

    def lucene_get_query(self):
        keywords = self.lucene_split_keywords(self.request.GET.get('k'))
        journals = self.lucene_split_arg(self.request.GET.get('j'))
        # Creating some empty strings
        keywords_str = ''
        journals_str = ''

        # It is badness to not search for anything
        if not keywords and not journals:
            raise BadRequest()

        if keywords:
            keywords_str = " AND ".join([" OR ".join(aa) for aa in keywords])

        # Deal with the case that there are no journals to be filtered by
        if journals:
           journals_str = ''.join(['journalID:(',' OR '.join(journals),')'])
           # If there are keywords then AND the journals to them
           if keywords:
               journals_str = ' AND '+journals_str
        return ''.join([keywords_str, journals_str])

    def lucene_search(self):
        query = self.lucene_get_query()
        resp = self.lucene_request(query)
        return self.lucene_process(resp)

    # TODO Behaviour of this method should be in scrapers/couch views
    def process_docs(self, lucene_docs):
        for d in lucene_docs:
            # Cannot use _id inside a Django template
            d['docid'] = d['_id']
            # Process the timestamp to produce a usable datetime object
            # TODO Need a reliable property to access for date
            try:
              if d.has_key('date_published') and d['date_published'] is not None:
                  d['date'] = datetime.datetime.fromtimestamp(d['date_published'])
              elif d.has_key('date_revised') and d['date_revised'] is not None:
                  d['date'] = datetime.datetime.fromtimestamp(d['date_revised'])
              elif d.has_key('date_received') and d['date_received'] is not None:
                  d['date'] = datetime.datetime.fromtimestamp(d['date_received'])
              else:
                  d['date'] = datetime.datetime.now()
            except TypeError:
              d['date'] = datetime.datetime.now()

            if 'citation' in d and 'journal' in d['citation']:
              d['journal'] = d['citation']['journal']
            elif 'categories' in d and 'arxiv' in d['categories']:
              d['journal'] = d['categories']['arxiv'][0] + " (arxiv)"

        return lucene_docs

    def get_context_data(self, **kwargs):
        """
        Return the context to the template
        """
        docs = self.process_docs(self.lucene_search())
        # Create the context structure
        context = {'docs': docs}
        return context

    def get(self, *args, **kwargs):
        """
        Returns the appropriate HttpResponse
        """
        try:
            return super(ArticlesView, self).get(*args, **kwargs)
        except BadRequest as e:
            return HttpResponse(e.message, status=400)


def latest(request, num):
    db = db_store

    num = min(int(num), 100)

    journals_s = request.GET.get('q')

    if journals_s:
      journals = journals_s.split('+')
    else:
      journals = None
   
    if 'last_ids' in request.GET: 
      last_ids = json.loads(request.GET['last_ids'])
    else:
      last_ids = {}

    if journals is not None:
      all_rows = []
      for journal in journals:
        if journal in last_ids:
          print journal, last_ids[journal]
          rows = db.view('articles/latest_journal', limit=num, include_docs=True, startkey=last_ids[journal][0], startkey_docid=last_ids[journal][1], endkey=[journal], skip=1, descending=True)
        else:
          rows = db.view('articles/latest_journal', limit=num, include_docs=True, endkey=[journal], startkey=[journal,{}], descending=True)

        rows_journal = rows.rows # list(rows[[journal,{}]:[journal]])
        #last_ids[journal] = (rows_journal[-1].key, rows_journal[-1].doc['_id'])
        all_rows += rows_journal

      all_rows = sorted(all_rows, key=lambda row: row.doc['date_published'], reverse=True)[:num]

      for row in all_rows:
        last_ids[row.key[0]] = (row.key, row.doc['_id'])
      
      last_ids_json = json.dumps(last_ids)
    else:
      if 'all' in last_ids:
        all_rows = list(db.view('articles/latest', limit=num, include_docs=True, startkey=last_ids['all'][0], startkey_docid=last_ids['all'][1], skip=1, descending=True))
      else:
        all_rows = list(db.view('articles/latest', limit=num, include_docs=True, descending=True))

      last_ids_json = json.dumps({'all': (all_rows[-1].key, all_rows[-1].doc['_id'])})
      
      all_rows = sorted(all_rows, key=lambda row: row.doc['date_published'], reverse=True)

    docs = []
    for row in all_rows:
        d = row.doc
        # Cannot use _id inside a Django template
        d['docid'] = d['_id']
        # Process the timestamp to produce a usable datetime object
        # TODO Need a reliable property to access for date
        try:
          if d.has_key('date_published') and d['date_published'] is not None:
              d.date = datetime.datetime.fromtimestamp(d['date_published'])
          elif d.has_key('date_revised') and d['date_revised'] is not None:
              d.date = datetime.datetime.fromtimestamp(d['date_revised'])
          elif d.has_key('date_received') and d['date_received'] is not None:
              d.date = datetime.datetime.fromtimestamp(d['date_received'])
          else:
              d.date = datetime.datetime.now()
        except TypeError:
          d.date = datetime.datetime.now()

        if 'citation' in d and 'journal' in d['citation']:
          d.journal = d['citation']['journal']
        elif 'categories' in d and 'arxiv' in d['categories']:
          d.journal = d['categories']['arxiv'][0] + " (arxiv)"

        docs.append(d)

    return render_to_response('search/article_list.html', {'docs': docs, 'last_ids_json': last_ids_json})

def journals(request):
  db = db_store
 
  rows = db.view('index/journals', group=True)

  if 'term' in request.GET:
    filter = clean_journal(request.GET['term'])
  else:
    filter = None

  return HttpResponse(json.dumps([row.key for row in rows if filter is None or
                                  filter in clean_journal(row.key)]),
                      content_type='application/json')

def journals_new(request):
  if 'term' in request.GET:
    filter = clean_journal(request.GET['term'])
  else:
    filter = None

  journals = []

  for doc in journal_doc_cache:
    if 'name' not in doc:
      continue

    for alias in doc['sorted_aliases']:
      if filter is not None and filter in alias[0]:
        journals.append((doc['name'], alias[1], doc.id))
        break
      elif filter is None:
        journals.append((doc['name'], alias[1], doc.id))
        break
  return HttpResponse(json.dumps(journals), content_type='application/json')


class JSONResponseMixin(object):
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        # TODO Add support for objects that cannot be serialized directly
        return json.dumps(context)

def articles_since(journals, timestamp=None):
    """
    Returns a dict of journal IDs and article counts
    Takes a list of journal IDs and a timestamp to count from
    """
    db = db_store
    output = {}

    #if timestamp is not None:
    timestamp = time.mktime(datetime.date.today().timetuple())

    # TODO Do this with one couch query?
    for journal_id in journals:
        rows = db.view('articles/latest_journal',
            include_docs=False,
            startkey=[journal_id, timestamp],
            endkey=[journal_id, {}],
            descending=False)
        output[journal_id] = len(rows)

    return output

class ArticleCountView(JSONResponseMixin, View):
    def articles_since(self, journals, timestamp=None):
        """
        Returns as JSON a dict of journal IDs and article counts
        Takes a list of journal IDs and a timestamp to count from
        """
        if timestamp:
            try:
                # TODO Should probably validate user supplied timestamp
                timestamp = int(timestamp)
            except ValueError:
                # TODO Should be doing this with exceptions
                return HttpResponse(status=400)

        return self.render_to_response(articles_since(journals, timestamp))

    def get(self, *args, **kwargs):
        """
        Returns as JSON a dict of journal IDs and article counts
        Takes a + separated string of journal IDs and a UNIX timestamp in s:
        If no timestamp is provided it gives count of articles published today
        """
        journals_s = self.request.GET.get('q')
        time_s = self.request.GET.get('time', None)
        if not journals_s:
            return HttpResponse(status=400)
        return self.articles_since(journals_s.split('+'), time_s)

    def post(self, *args, **kwargs):
        """
        Returns as JSON a dict of journal IDs and article counts
        Takes a JSON serialize query object and a UNIX timestamp in s
        """
        query = self.request.POST.get('q')
        time_s = self.request.POST.get('time')
        if not query:
            return HttpResponse(status=400)
        return self.articles_since(json.loads(query.keys()), time_s)
