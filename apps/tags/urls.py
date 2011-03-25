from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("tags.views",
    url(r"^tags/add/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$", "add", name="add_tags"),
    url(r"^tags/delete/?$", "delete", name="delete_tags"),
)
