from django.conf.urls.defaults import patterns, url
from lessons.views.forms.define import Define
from lessons.views.forms.organize import Organize, Image
from lessons.views.forms.outline import Outline
from lessons.views.new import NewLesson


urlpatterns = patterns("",
    url(r"^new$", NewLesson.as_view(), name="new"),
    url(r"^edit/(?P<lesson_id>\d+)/define$", Define.as_view(), name="edit_define"),
    url(r"^edit/(?P<lesson_id>\d+)/organize$", Organize.as_view(), name="edit_organize"),
    url(r"^edit/(?P<lesson_id>\d+)/upload-image$", Image.as_view(action="upload"), name="edit_image_upload"),
    url(r"^edit/(?P<lesson_id>\d+)/remove-image$", Image.as_view(action="remove"), name="edit_image_remove"),
    url(r"^edit/(?P<lesson_id>\d+)/outline$", Outline.as_view(), name="edit_outline"),
)