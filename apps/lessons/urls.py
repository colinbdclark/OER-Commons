from django.conf.urls.defaults import patterns, url
from lessons.views.forms.define import Define
from lessons.views.forms.organize import Organize
from lessons.views.new import NewLesson


urlpatterns = patterns("",
    url(r"^new$", NewLesson.as_view(), name="new"),
    url(r"^edit/(?P<lesson_id>\d+)/define$", Define.as_view(), name="edit_define"),
#    url(r"^edit/(?P<lesson_id>\d+)/upload$", LessonImage.as_view(action="upload"), name="lesson_image_upload"),
#    url(r"^edit/(?P<lesson_id>\d+)/remove$", LessonImage.as_view(action="remove"), name="lesson_image_remove"),
    url(r"^edit/(?P<lesson_id>\d+)/organize$", Organize.as_view(), name="edit_organize"),
)