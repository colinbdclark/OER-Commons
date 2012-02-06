from authoring.views.write import Write
from authoring.views.media import MediaUpload, LoadEmbed
from authoring.views.new import New
from authoring.views.view import ViewAuthoredMaterial
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
    url(r"new$", New.as_view(), name="new"),
    url(r"edit/(?P<material_id>\d+)$", Write.as_view(), name="write"),
    url(r"edit/(?P<material_id>\d+)/upload$", MediaUpload.as_view(), name="upload"),
    url(r"load-embed$", LoadEmbed.as_view(), name="load-embed"),
    url(r"(?P<material_id>\d+)$", ViewAuthoredMaterial.as_view(), name="view"),
)
