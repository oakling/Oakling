from django.http import HttpResponse
from django.shortcuts import render_to_response
import urllib

import re
import json

from django.template import RequestContext
from lib.search import citeulike, mendeley, arxiv
import Queue
import threading
import itertools
import couchdb
import datetime

def save_search(request):
    """
    Stores searches the user explicitly requests to be saved
    """
    query = request.GET.get('q')
    if not query:
        # Without a query to save this is a bad request
        return HttpResponse(status=400)
    # Check the user has a saved search list
    if not request.session.get('saved_searches'):
        # Make an empty list
        request.session['saved_searches'] = []
    # Add the query to the users saved_search list
    request.session['saved_searches'].append(query)
    # Success but no response to give
    return HttpResponse(status=204)

def latest(request, num):
    db = couchdb.Server()['store']

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
        if d.has_key('date_published'):
            d.date = datetime.datetime.fromtimestamp(d['date_published'])
        elif d.has_key('date_revised'):
            d.date = datetime.datetime.fromtimestamp(d['date_revised'])
        elif d.has_key('date_received'):
            d.date = datetime.datetime.fromtimestamp(d['date_received'])
        else:
            d.date = datetime.datetime.now()

        if 'citation' in d and 'journal' in d['citation']:
          d.journal = d['citation']['journal']
        elif 'categories' in d and 'arxiv' in d['categories']:
          d.journal = d['categories']['arxiv'][0]

        docs.append(d)

    print last_ids_json

    return render_to_response('search/article_list.html', {'docs': docs, 'last_ids_json': last_ids_json})

def clean_journal(s):
  # keep only alphanumeric characters for comparison purposes
  return re.sub('\s+', ' ', re.sub('[^a-z]', ' ', s.lower()))

def journals(request):
  db = couchdb.Server()['store']
  filter = clean_journal(request.GET.get('term', None))

  rows = db.view('index/journals', group=True)

  return HttpResponse(json.dumps([row.key for row in rows if filter is None or
                                 filter in clean_journal(row.key)]),
                      content_type='application/json')
