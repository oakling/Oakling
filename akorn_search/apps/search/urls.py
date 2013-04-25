from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^search/$', views.home, name='home'),
    url(r'^doc/(?P<id>[A-Za-z0-9]+)$', views.doc, name='viewdoc'),
    url(r'^journals/(?P<id>.*)$', views.journal, name='viewjournal'),
)

