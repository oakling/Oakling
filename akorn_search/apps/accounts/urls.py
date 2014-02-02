from django.conf.urls import patterns, url

from apps.accounts.views import RegisterView

urlpatterns = patterns('',
    url(r'^register/', RegisterView.as_view(), name='register'),
)
