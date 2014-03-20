from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.SimulatorView.as_view(), name='simulator'),
)
