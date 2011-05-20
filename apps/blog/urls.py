from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("blog.views",
    url(u"^blog/?$", "blog", name="blog"),
)
