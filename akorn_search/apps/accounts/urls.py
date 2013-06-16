from django.conf.urls.defaults import patterns, url

from apps.accounts.views import RegisterView

urlpatterns = patterns('',
    url(r'^register/', RegisterView.as_view(), name='register'),
)
