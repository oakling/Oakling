from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^search/$', views.search, name='search'),
    url(r'^doc/(?P<id>[A-Za-z0-9]+)$', views.doc, name='viewdoc'),
    url(r'^journal/(?P<id>[A-Za-z0-9]+)$', views.journal, name='viewjournal'),
    url(r'^$', views.home, name='home'),
)
