from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^backend/journals$', views.backend_journals, name='backend_journals'),
    url(r'^backend/journals/(?P<journal_id>.*)$', views.backend_journal, name='backend_journal'),

    url(r'^search/$', views.home, name='home'),
    url(r'^doc/(?P<id>[A-Za-z0-9]+)$', views.doc, name='viewdoc'),
    url(r'^journals/(?P<id>.*)$', views.journal, name='viewjournal'),
)

