from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("rating.views",
    url(r"rate/?$", "rate", name="rate_item"),
)
