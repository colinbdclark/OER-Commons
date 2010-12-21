from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("information.views",
    url(r"^information/?$", "information", name="information"),
    url(r"^help/?$", "help", name="help"),
    url(r"^about/?$", "about", name="about"),
)
