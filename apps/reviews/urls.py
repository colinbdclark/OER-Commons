from django.conf.urls.defaults import patterns, url

add_review_patterns = patterns("reviews.views",
    url(r"^/(?P<slug>[^/]+)/review/?$", "add", name="add_review"),
)
