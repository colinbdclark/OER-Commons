from django.conf.urls.defaults import patterns, url

saved_item_patterns = patterns("saveditems.views",
    url(r"^/(?P<slug>[^/]+)/save/?$", "save", name="save_item"),
    url(r"^/(?P<slug>[^/]+)/unsave/?$", "unsave", name="unsave_item"),
)
