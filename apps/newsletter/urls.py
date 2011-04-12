from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("newsletter.views",
   url(r"^subscribe/?$", "subscribe", name="subscribe"),
)