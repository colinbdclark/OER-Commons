from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("api.views",
   url("^search/?$", "search.search"),
)
