from django.conf.urls import patterns, url

from apps.accounts.views import JSONRegisterView, RegisterView

urlpatterns = patterns('',
    url(r'^register/', RegisterView.as_view(), name='register'),
    url(r'^register.json', JSONRegisterView.as_view(), name='register_json'),
)
