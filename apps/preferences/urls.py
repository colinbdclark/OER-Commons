from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("preferences.views",
    url(r"^preferences/?$", "preferences", name="preferences"),                       
)