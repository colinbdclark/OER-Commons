from authoring.views.edit import Edit
from authoring.views.media import MediaUpload, LoadEmbed
from authoring.views.new import New
from authoring.views.view import ViewAuthoredMaterial
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
    url(r"new$", New.as_view(), name="new"),
    url(r"edit/(?P<pk>\d+)$", Edit.as_view(), name="edit"),
    url(r"edit/(?P<pk>\d+)/upload$", MediaUpload.as_view(), name="upload"),
    url(r"load-embed$", LoadEmbed.as_view(), name="load-embed"),
    url(r"(?P<pk>\d+)$", ViewAuthoredMaterial.as_view(), name="view"),
    url(r"(?P<pk>\d+)/preview$", ViewAuthoredMaterial.as_view(preview=True), name="preview"),
)
