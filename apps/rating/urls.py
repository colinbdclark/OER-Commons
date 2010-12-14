from django.conf.urls.defaults import patterns, url

rating_patterns = patterns("rating.views",
    url(r"^/(?P<slug>[^/]+)/rate/?$", "rate", name="rate_item"),
)
