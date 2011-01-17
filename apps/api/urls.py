from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("api.views",
   url("^search/?$", "search.search"),
   url("^get_tags/?$", "get_tags.get_tags"),
   url("^set_tags/?$", "set_tags.set_tags"),
   url("^get_review/?$", "get_review.get_review"),
   url("^set_review/?$", "set_review.set_review"),
)
