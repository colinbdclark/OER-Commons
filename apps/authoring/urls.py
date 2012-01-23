from authoring.views.edit import  Edit
from authoring.views.media import MediaUpload
from authoring.views.new import New
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
    url(r"new$", New.as_view(), name="new"),
    url(r"edit/(?P<material_id>\d+)$", Edit.as_view(), name="edit"),
    url(r"edit/(?P<material_id>\d+)/upload$", MediaUpload.as_view(), name="upload"),
)
