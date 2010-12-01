from django.conf import settings
from django.conf.urls.defaults import patterns, handler500, handler404, url, \
    include
from django.contrib import admin
from django.views.generic.simple import direct_to_template


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "project.views.frontpage", name="frontpage"),
    url(r'', include('materials.urls', app_name=None, namespace="materials")),
)


# Dummy URL should be replaced with real ones later.
# We place them here because we need then in {% url %} tags.
urlpatterns += patterns('',
    url(r'^registration$', "project.views.frontpage", name="registration"),
    url(r'^login$', "project.views.frontpage", name="auth_login"),
    url(r'^profile$', "project.views.frontpage", name="profile_edit"),
    url(r'^logout$', "project.views.frontpage", name="auth_logout"),
    url(r'^feedback$', "project.views.frontpage", name="feedback"),
    url(r'^information$', "project.views.frontpage", name="information"),
    url(r'^contribute$', "project.views.frontpage", name="contribute"),
    url(r'^my$', "project.views.frontpage", name="user_items"), # TODO! Set up redirect /portfolio -> /my
    url(r'^advanced-search$', "project.views.frontpage", name="materials_advanced_search"),
    url(r'^(?P<microsite>[^/]+)$', "project.views.frontpage", name="microsite"),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
    )
