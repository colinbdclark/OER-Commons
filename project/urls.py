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
from oai.oer.oai_dc import OAIDublinCore
from oai.oer.oer_recommender import OERRecommender
from oai.oer.oer_submissions import OERSubmissions
from oai.oer.repository import OERRepository
from oai.oer.oai_oer2 import OAIOER2


admin.autodiscover()


class GenericSitemap(BaseGenericSitemap):
    limit = 1000


sitemaps = {
    'courses': GenericSitemap(dict(queryset=Course.objects.filter(workflow_state=PUBLISHED_STATE), date_field="published_on")),
    'libraries': GenericSitemap(dict(queryset=Library.objects.filter(workflow_state=PUBLISHED_STATE), date_field="published_on")),
    'community': GenericSitemap(dict(queryset=CommunityItem.objects.filter(workflow_state=PUBLISHED_STATE), date_field="published_on")),
}


oai_metadata_formats = {
    "oai_dc": OAIDublinCore,
    "oer_recommender": OERRecommender,
    "oer_submissions": OERSubmissions,
    "oai_oer2": OAIOER2,
}

repository = OERRepository(u"OER Commons Repository", "oercommons.org", oai_metadata_formats, "info@oercommons.org")


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "project.views.frontpage", name="frontpage"),
    url(r'^contribute$', "project.views.contribute", name="contribute"),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^robots.txt$', 'django.views.generic.simple.direct_to_template', {'template': "robots.txt", "mimetype": "text/plain"}),
    url(r'^(?:(?P<microsite>\w+)/)?oai/?$', 'oai.views.oai', {'repository': repository}, name="oai"),
    url(r'^oerr.xsd$', 'django.views.generic.simple.direct_to_template', {'template': "oai/oer/oerr.xsd", "mimetype": "text/xml"}, name="oerr.xsd"),
    url(r'^oers.xsd$', 'django.views.generic.simple.direct_to_template', {'template': "oai/oer/oers.xsd", "mimetype": "text/xml"}, name="oers.xsd"),
    url(r'', include('users.urls', app_name=None, namespace="users")),
    url(r'', include('feedback.urls')),
    url(r'', include('information.urls')),
    url(r'', include('sendthis.urls')),
    url(r'^my', include('myitems.urls', app_name=None, namespace="myitems")), # TODO! Set up redirect /portfolio -> /my
    url(r'^savedsearches', include('savedsearches.urls', app_name=None, namespace="savedsearches")),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^sentry/', include('sentry.urls')),
    url(r'', include('stats.urls')),
    url(r'', include('materials.urls', app_name=None, namespace="materials")),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
    )
