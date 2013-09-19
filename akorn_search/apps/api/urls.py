from django.conf.urls import patterns, include, url
from .views import JournalAutoCompleteView, DeleteSavedSearchView,\
    ArticlesView, SavedSearchView, ArticleCountView

urlpatterns = patterns('',
    url(r'^journals$', JournalAutoCompleteView.as_view(), name='journals'),
    url(r'^articles$', ArticlesView.as_view(), name='articles'),
    url(r'^searches$', SavedSearchView.as_view(), name='save_search'),
    url(r'^remove_search$', DeleteSavedSearchView.as_view(), name='remove_search'),
    url(r'^num_new$', ArticleCountView.as_view(), name='num_new'),
)
