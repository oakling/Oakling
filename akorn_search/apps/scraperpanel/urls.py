from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^backend/scrapers$', views.backend_scrapers, name='backend_scrapers'),
    url(r'^backend/scraper_detail/(?P<scraper_module>[A-Za-z._]+)$', views.backend_scraper_detail, name='backend_scraper_detail'),
    url(r'^backend/rescrape$', views.backend_rescrape, name='backend_rescrape'),
)
