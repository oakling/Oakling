from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^backend/journals$', views.backend_journals, name='backend_journals'),
    url(r'^backend/journals/(?P<journal_id>.*)$', views.backend_journal,\
        name='backend_journal'),
    url(r'^backend/scrapers$', views.backend_scrapers, name='backend_scrapers'),
    url(r'^search/$', views.HomeView.as_view(), name='home'),
    url(r'^doc/(?P<id>[A-Za-z0-9]+)$', views.DocView.as_view(), name='viewdoc'),
    url(r'^journals/(?P<id>.*)$', views.JournalView.as_view(), name='viewjournal'),
)
