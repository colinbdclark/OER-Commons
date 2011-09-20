from django.conf.urls.defaults import patterns, url
from rubrics.manage.views import Login, Index


urlpatterns = patterns("",
    url(r"^login$", Login.as_view(), name="login"),
    url(r"^$", Index.as_view(), name="index"),
)
