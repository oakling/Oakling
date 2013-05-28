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
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('apps.api.urls', namespace='api')),
    url(r'^signup/', include('lazysignup.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name="auth_logout"),
    url(r'^login/$', 'django.contrib.auth.views.login',
        name="auth_login"),
    url(r'', include('apps.search.urls', namespace='search')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^'+settings.STATIC_URL[1:]+'(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}),
    )
