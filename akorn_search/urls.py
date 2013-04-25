from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# TODO Should be handled by a catch-all, but can't because of search app
urlpatterns = patterns('django.contrib.flatpages.views',
    url(r'^about/$', 'flatpage', {'url': '/about/'}, name='about'),
    url(r'^volunteer/$', 'flatpage', {'url': '/volunteer/'}, name='volunteer'),
    url(r'^$', 'flatpage', {'url': '/'}, name='main'),
)

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'akorn.views.home', name='home'),
    # url(r'^akorn/', include('akorn.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('apps.api.urls', namespace='api')),
    url(r'', include('apps.search.urls', namespace='search')),
    url(r'', include('apps.backend.urls', namespace='backend'))
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^'+settings.STATIC_URL[1:]+'(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}),
    )
