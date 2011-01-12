from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("sendthis.views",
   url(r"^send-this/?$", "send", name="send-this"),
)
