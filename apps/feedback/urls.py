from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("feedback.views",
    url(r"^feedback/?$", "feedback", name="feedback"),
)
