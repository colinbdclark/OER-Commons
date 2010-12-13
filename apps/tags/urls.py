from django.conf.urls.defaults import patterns, url


add_tags_patterns = patterns("tags.views",
    url(r"^/(?P<slug>[^/]+)/tags/?$", "add", name="add_tags"),
)
