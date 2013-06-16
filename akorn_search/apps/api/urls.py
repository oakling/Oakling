from django.conf.urls.defaults import patterns, include, url

from .views import latest, journals_new, DeleteSavedSearchView,\
    ArticlesView, SavedSearchView, ArticleCountView

urlpatterns = patterns('',
    url(r'^latest/(?P<num>[0-9]+)$', latest, name='latest'),
    url(r'^journals_new$', journals_new, name='journals_new'),
    url(r'^articles$', ArticlesView.as_view(), name='articles'),
    url(r'^save_search$', SavedSearchView.as_view(), name='save_search'),
    url(r'^remove_search$', DeleteSavedSearchView.as_view(), name='remove_search'),
    url(r'^num_new$', ArticleCountView.as_view(), name='num_new'),
)
