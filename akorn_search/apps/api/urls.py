from django.conf.urls import patterns, include, url
from .views import JournalAutoCompleteView, DeleteSavedSearchView,\
    ArticlesView, ArticlesViewXML, SavedSearchView, ArticleCountView,\
    LoginView, JSONRegisterView

urlpatterns = patterns('',
    url(r'^login$', LoginView.as_view(), name='api_login'),
    url(r'^journals$', JournalAutoCompleteView.as_view(), name='journals'),
    url(r'^articles$', ArticlesView.as_view(), name='articles'),
    url(r'^articles.xml$', ArticlesViewXML.as_view(), name='articles.xml'),
    url(r'^searches$', SavedSearchView.as_view(), name='save_search'),
    url(r'^remove_search$', DeleteSavedSearchView.as_view(), name='remove_search'),
    url(r'^num_new$', ArticleCountView.as_view(), name='num_new'),
    url(r'^register', JSONRegisterView.as_view(), name='register_json'),
)
