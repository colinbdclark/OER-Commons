from django.conf import settings
from django.conf.urls.defaults import patterns, handler500, handler404, url, \
    include
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from oai.oer.oai_dc import OAIDublinCore
from oai.oer.oai_oer2 import OAIOER2
from oai.oer.oer_recommender import OERRecommender
from oai.oer.oer_submissions import OERSubmissions
from oai.oer.repository import OERRepository
from sitemap import sitemaps


admin.autodiscover()


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
    url(r'^honeypot/', "project.views.honeypot", name="honeypot_value"),
    url(r'^(?:(?P<microsite>\w+)/)?oai/?$', 'oai.views.oai', {'repository': repository}, name="oai"),
    url(r'^oerr.xsd$', 'django.views.generic.simple.direct_to_template', {'template': "oai/oer/oerr.xsd", "mimetype": "text/xml"}, name="oerr.xsd"),
    url(r'^oers.xsd$', 'django.views.generic.simple.direct_to_template', {'template': "oai/oer/oers.xsd", "mimetype": "text/xml"}, name="oers.xsd"),
    url(r'', include('utils.urls', app_name=None, namespace="utils")),
    url(r'', include('users.urls', app_name=None, namespace="users")),
    url(r'', include('feedback.urls')),
    url(r'', include('information.urls')),
    url(r'', include('sendthis.urls')),
    url(r'', include('tags.urls', app_name=None, namespace="tags")),
    url(r'', include('rating.urls', app_name=None, namespace="rating")),
    url(r'', include('preferences.urls', app_name=None, namespace="preferences")),
    url(r'', include('curriculum.urls', app_name=None, namespace="curriculum")),
    url(r'^my', include('myitems.urls', app_name=None, namespace="myitems")), # TODO! Set up redirect /portfolio -> /my
    url(r'^savedsearches', include('savedsearches.urls', app_name=None, namespace="savedsearches")),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^sentry/', include('sentry.urls')),
    url(r'', include('stats.urls')),
    url(r'', include('newsletter.urls', app_name=None, namespace="newsletter")),
    url(r'', include('materials.urls', app_name=None, namespace="materials")),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
    )
