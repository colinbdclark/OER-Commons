from django.conf import settings
from django.conf.urls.defaults import patterns, handler500, handler404, url, \
    include
from django.contrib import admin
from django.views.generic.simple import direct_to_template


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "project.views.frontpage", name="frontpage"),
    url(r'', include('users.urls', app_name=None, namespace="users")),
    url(r'', include('materials.urls', app_name=None, namespace="materials")),
    url(r'', include('feedback.urls')),
    url(r'^my', include('myitems.urls', app_name=None, namespace="myitems")), # TODO! Set up redirect /portfolio -> /my
    url(r'^savedsearches', include('savedsearches.urls', app_name=None, namespace="savedsearches")),
)


# Dummy URL should be replaced with real ones later.
# We place them here because we need then in {% url %} tags.
urlpatterns += patterns('',
    url(r'^information$', "project.views.frontpage", name="information"),
    url(r'^contribute$', "project.views.frontpage", name="contribute"),
    url(r'^(?P<microsite>[^/]+)$', "project.views.frontpage", name="microsite"),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
    )
