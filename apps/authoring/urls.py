from authoring.models import AuthoredMaterial
from authoring.views.delete import Delete, DeleteDraft
from authoring.views.edit import Edit
from authoring.views.media import MediaUpload, LoadEmbed
from authoring.views.new import New
from authoring.views.pdf import AsPdf
from authoring.views.view import ViewFullAuthoredMaterial
from django.conf.urls.defaults import patterns, url
from materials.views.view_item import ViewItem


urlpatterns = patterns("",
    url(r"^new$", New.as_view(), name="new"),
    url(r"^edit/(?P<pk>\d+)$", Edit.as_view(), name="edit"),
    url(r"^edit/(?P<pk>\d+)/upload$", MediaUpload.as_view(), name="upload"),
    url(r"^delete/(?P<pk>\d+)$", Delete.as_view(), name="delete"),
    url(r"^delete-draft/(?P<pk>\d+)$", DeleteDraft.as_view(), name="delete-draft"),
    url(r"^load-embed$", LoadEmbed.as_view(), name="load-embed"),
    url(r"^(?P<pk>\d+)(?:-(?P<slug>[^/]+))?$", ViewItem.as_view(model=AuthoredMaterial), name="view"),
    url(r"^(?P<pk>\d+)(?:-(?P<slug>[^/]+))?/view$", ViewFullAuthoredMaterial.as_view(), name="view_full"),
    url(r"^(?P<pk>\d+)(?:-(?P<slug>[^/]+))?/pdf", AsPdf.as_view(), name="pdf"),
    url(r"^(?P<pk>\d+)/preview$", ViewFullAuthoredMaterial.as_view(preview=True), name="preview"),
)
