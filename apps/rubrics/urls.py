from django.conf.urls.defaults import patterns, url
from rubrics.views import Intro, Rubrics, Results, Align


urlpatterns = patterns("",
    url(r"^evaluate$", Intro.as_view(), name="evaluate_intro"),
    url(r"^evaluate/(?P<content_type_id>\d+)/(?P<object_id>\d+)$", Rubrics.as_view(), name="evaluate_rubrics"),
    url(r"^evaluate/(?P<content_type_id>\d+)/(?P<object_id>\d+)/align", Align.as_view(), name="evaluate_align"),
    url(r"^evaluate/(?P<content_type_id>\d+)/(?P<object_id>\d+)/results", Results.as_view(), name="evaluate_results"),
)
