from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^latest/(?P<num>[0-9]+)$', views.latest, name='latest'),
    url(r'^journals$', views.journals, name='journals'),
    url(r'^save_search', views.save_search, name='save_search'),
    url(r'^remove_search', views.del_saved_search, name='remove_search'),
)
