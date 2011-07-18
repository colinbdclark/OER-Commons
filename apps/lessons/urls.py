from django.conf.urls.defaults import patterns, url
from lessons.views.edit import EditLesson
from lessons.views.new import NewLesson


urlpatterns = patterns("",
    url(r"^new$", NewLesson.as_view(), name="new"),
    url(r"^edit/(?P<lesson_id>\d+)$", EditLesson.as_view(), name="edit"),
)