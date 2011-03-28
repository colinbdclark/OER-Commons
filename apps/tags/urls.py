from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("tags.views",
    url(r"^tags/add/(\w+)/(\w+)/(\d+)/?$", "add", name="add_tags"),
    url(r"^tags/delete/?$", "delete", name="delete_tags"),
    url(r"^tags/get-tags/(\w+)/(\w+)/(\d+)/?$", "get_tags", name="get_tags"),
)
