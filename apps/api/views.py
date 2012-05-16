from django.http import HttpResponse
from django.shortcuts import render_to_response

import json

from django.template import RequestContext
from lib.search import citeulike, mendeley, arxiv
import Queue
import threading
import itertools
import couchdb

def latest(request):
  db = couchdb.Server()['store']

  rows = db.view('articles/latest', limit=10, include_docs=True)

  return json.dumps([row.doc for row in rows])
