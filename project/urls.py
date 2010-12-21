from django.conf import settings
from django.conf.urls.defaults import patterns, handler500, handler404, url, \
    include
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap as BaseGenericSitemap
from django.views.generic.simple import direct_to_template
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from materials.models.material import PUBLISHED_STATE


admin.autodiscover()


class GenericSitemap(BaseGenericSitemap):
    limit = 1000


sitemaps = {
    'courses': GenericSitemap(dict(queryset=Course.objects.filter(workflow_state=PUBLISHED_STATE), date_field="published_on")),
    'libraries': GenericSitemap(dict(queryset=Library.objects.filter(workflow_state=PUBLISHED_STATE), date_field="published_on")),
    'community': GenericSitemap(dict(queryset=CommunityItem.objects.filter(workflow_state=PUBLISHED_STATE), date_field="published_on")),
}


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "project.views.frontpage", name="frontpage"),
    url(r'^contribute$', "project.views.contribute", name="contribute"),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'', include('users.urls', app_name=None, namespace="users")),
    url(r'', include('materials.urls', app_name=None, namespace="materials")),
    url(r'', include('feedback.urls')),
    url(r'', include('information.urls')),
    url(r'^my', include('myitems.urls', app_name=None, namespace="myitems")), # TODO! Set up redirect /portfolio -> /my
    url(r'^savedsearches', include('savedsearches.urls', app_name=None, namespace="savedsearches")),
)


# Dummy URL should be replaced with real ones later.
# We place them here because we need then in {% url %} tags.
urlpatterns += patterns('',
    url(r'^(?P<microsite>[^/]+)$', "project.views.frontpage", name="microsite"),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
    )
