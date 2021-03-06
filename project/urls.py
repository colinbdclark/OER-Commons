from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from oai.oer.oai_dc import OAIDublinCore
from oai.oer.oai_oer2 import OAIOER2
from oai.oer.oer_recommender import OERRecommender
from oai.oer.oer_submissions import OERSubmissions
from oai.oer.repository import OERRepository
from project.views import Contribute
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
    url(r'^contribute$', Contribute.as_view(), name="contribute"),
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
    url(r'', include('reviews.urls', app_name=None, namespace="reviews")),
    url(r'', include('curriculum.urls', app_name=None, namespace="curriculum")),
    url(r'', include('rubrics.urls', app_name=None, namespace="rubrics")),
    url(r'^authoring/', include('authoring.urls', app_name=None, namespace="authoring")),
    url(r'^rubrics/manage/', include('rubrics.manage.urls', app_name=None, namespace="rubrics_manage")),
    url(r'^my', include('myitems.urls', app_name=None, namespace="myitems")),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'^sentry/', include('sentry.urls')),
    url(r'^mailchimp/', include('mailchimp.urls')),
    url(r'', include('stats.urls')),
    url(r'', include('newsletter.urls', app_name=None, namespace="newsletter")),
    url(r'', include('materials.urls', app_name=None, namespace="materials")),
    url(r'^saveditems', include('saveditems.urls', app_name=None, namespace="saveditems")),
    url(r'^jsurls.js$', 'django_js_utils.views.jsurls', name='jsurls'),
)

if settings.DEBUG:
    if "cssreload" in settings.INSTALLED_APPS:
        urlpatterns += patterns('',
            url(r"^", include("cssreload.urls")),
        )
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
    )
