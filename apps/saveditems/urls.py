from django.conf.urls.defaults import patterns, url
from django_js_utils.core import expose_to_js

urlpatterns = patterns("saveditems.views",
    expose_to_js(url(r"^/save$", "save", name="save_item")),
    expose_to_js(url(r"^/unsave$", "unsave", name="unsave_item")),
)
