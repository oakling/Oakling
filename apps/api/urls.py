from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^latest$', views.latest, name='latest'),
)
