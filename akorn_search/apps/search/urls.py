from django.conf.urls.defaults import patterns, url
import views
from lazysignup.decorators import allow_lazy_user

urlpatterns = patterns('',
    url(r'^search/$', allow_lazy_user(views.HomeView.as_view()), name='home'),
    url(r'^doc/(?P<id>[A-Za-z0-9]+)$', allow_lazy_user(views.DocView.as_view()), name='doc'),
    url(r'^journal/(?P<id>.*)$', allow_lazy_user(views.JournalView.as_view()), name='journal'),
)
