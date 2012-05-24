from django.http import HttpResponse
from django.shortcuts import render_to_response

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

def journals(request):
  db = couchdb.Server()['store']

  rows = db.view('index/journals', group=True)

  return HttpResponse(json.dumps([row.key for row in rows]), content_type='application/json')
