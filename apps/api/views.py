from django.http import HttpResponse
from django.shortcuts import render_to_response

import re
import json

from django.template import RequestContext
from lib.search import citeulike, mendeley, arxiv
import Queue
import threading
import itertools
import couchdb

def latest(request, num):
  db = couchdb.Server()['store']

  num = min(int(num), 100)

  rows = db.view('articles/latest', limit=num, include_docs=True, descending=True)

  return HttpResponse(json.dumps([row.doc for row in rows]), content_type='application/json')

def clean_journal(s):
  # keep only alphanumeric characters for comparison purposes
  return re.sub('\s+', ' ', re.sub('[^a-z]', ' ', s.lower()))

def journals(request):
  db = couchdb.Server()['store']
  filter = clean_journal(request.GET.get('filter', None))

  rows = db.view('index/journals', group=True)

  return HttpResponse(json.dumps([row.key for row in rows if filter is None or filter in clean_journal(row.key)]), content_type='application/json')
