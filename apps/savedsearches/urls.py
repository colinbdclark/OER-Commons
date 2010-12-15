from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("savedsearches.views",
   url(r"^/save/?$", "save", name="save"),
   url(r"^/(?P<id>\d+)/unsave/?$", "unsave", name="unsave"),
)
