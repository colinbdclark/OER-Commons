from django.conf.urls.defaults import url, patterns


urlpatterns = patterns("utils.views",
   url(r'^autocomplete/(\w+)/(\w+)/(\w+)/?$', "autocomplete", name="autocomplete"),
)

