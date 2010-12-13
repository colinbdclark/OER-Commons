from django.conf.urls.defaults import patterns, url

add_note_patterns = patterns("notes.views",
    url(r"^/(?P<slug>[^/]+)/note/?$", "add", name="add_note"),
)
