from django.shortcuts import render_to_response
from django.template import RequestContext
from libs import citeulike, mendeley, arxiv, adsabs, gscholar

def home(request):
    return render_to_response('search/home.html',
                              context_instance=RequestContext(request))

def search(request):
    if 'q' in request.GET:
        api_results = [ {'name':'Citeulike',
                         'id':'citeulike',
                         'results':citeulike.search(request.GET['q'])},
                       {'name':'Arxiv',
                        'id':'arxiv',
                        'results':arxiv.search(request.GET['q'])},
                       {'name':'Mendeley',
                        'id':'mendeley',
                        'results':mendeley.search(request.GET['q'])},
                       {'name':'ADSABS',
                        'id':'adsabs',
                        'results':adsabs.search(request.GET['q'])},
                       {'name':'Google Scholar',
                        'id':'gscholar',
                        'results':gscholar.search(request.GET['q'])},
                      ]
        return render_to_response('search/results.html',
            {'api_results':api_results},
            context_instance=RequestContext(request))
