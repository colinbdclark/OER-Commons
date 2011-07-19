from django.conf.urls.defaults import patterns, url
from lessons.views.edit import EditLesson, LessonImage
from lessons.views.new import NewLesson


urlpatterns = patterns("",
    url(r"^new$", NewLesson.as_view(), name="new"),
    url(r"^edit/(?P<lesson_id>\d+)$", EditLesson.as_view(), name="edit"),
    url(r"^edit/(?P<lesson_id>\d+)/upload$", LessonImage.as_view(action="upload"), name="lesson_image_upload"),
    url(r"^edit/(?P<lesson_id>\d+)/remove$", LessonImage.as_view(action="remove"), name="lesson_image_remove"),
)