from django.shortcuts import render_to_response
from django.template import RequestContext
from libs import citeulike, mendeley, arxiv
import Queue
import threading

def home(request):
    return render_to_response('search/home.html',
                              context_instance=RequestContext(request))

class SearchThread(threading.Thread):
    """Threaded access to search api."""
    def __init__(self, queue, output):
        threading.Thread.__init__(self)
        self.queue = queue
        self.output = output

    def run(self):
        while True:
            api, query = self.queue.get()

            results = api['module'].search(query)

            self.output.append({'name':api['name'],
                                'id':api['id'],
                                'results':results})
            self.queue.task_done()

def search(request):
    if 'q' in request.GET:
        queue = Queue.Queue()
        api_results = []

        apis = [ {'name':'Citeulike',
                  'id':'citeulike',
                  'module':citeulike},
                {'name':'Arxiv',
                 'id':'arxiv',
                 'module':arxiv},
                {'name':'Mendeley',
                 'id':'mendeley',
                 'module':mendeley},
                # ADSABS is too slow
                #{'name':'ADSABS',
                # 'id':'adsabs',
                # 'results':adsabs.search(request.GET['q'])},
                # Google Scholar does not like AWS
                #{'name':'Google Scholar',
                # 'id':'gscholar',
                # 'results':gscholar.search(request.GET['q'])},
               ]

        for api in apis:
            t = SearchThread(queue, api_results)
            t.setDaemon(True)
            t.start()

        for api in apis:
            queue.put((api, request.GET['q']))

        queue.join()

        return render_to_response('search/results.html',
                                  {'api_results':api_results},
                                  context_instance=RequestContext(request))
