from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("myitems.views",
  url(r"^/?$", "saved", name="myitems"),
  url(r"^/rated/?$", "rated", name="rated"),
  url(r"^/tagged/?$", "tagged", name="tagged"),
  url(r"^/reviewed/?$", "reviewed", name="reviewed"),
  url(r"^/noted/?$", "noted", name="noted"),
  url(r"^/submitted/?$", "submitted", name="submitted"),
  url(r"^/searches/?$", "searches", name="searches"),
)
