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

def latest(request, num):
    db = couchdb.Server()['store']

    num = min(int(num), 100)

    journals_s = request.GET.get('q')

    if journals_s:
      journals = journals_s.split('+')
    else:
      journals = None

    print journals

    if journals is not None:
      all_rows = []
      for journal in journals:
        rows = db.view('articles/latest_journal', limit=num, include_docs=True, descending=True)
        rows_journal = rows[[journal,{}]:[journal]]
        all_rows += rows_journal

      all_rows = sorted(all_rows, key=lambda row: row.doc['date_published'], reverse=True)
    else:
      all_rows = db.view('articles/latest', limit=num, include_docs=True, descending=True)
      
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

    return render_to_response('search/article_list.html', {'docs': docs})

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
