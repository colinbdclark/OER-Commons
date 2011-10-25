from django.conf.urls.defaults import patterns, url
from reviews.views import ReviewView


urlpatterns = patterns("reviews.views",
    url(r"^review/(?P<content_type_id>\d+)/(?P<object_id>\d+)$", ReviewView.as_view(), name="review"),
)
