from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^search/$', views.HomeView.as_view(), name='home'),
    url(r'^doc/(?P<id>[A-Za-z0-9]+)$', views.DocView.as_view(), name='viewdoc'),
    url(r'^journals/(?P<id>.*)$', views.JournalView.as_view(), name='viewjournal'),
)
