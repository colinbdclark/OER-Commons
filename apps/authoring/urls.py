from authoring.views.describe import Describe
from authoring.views.submit import Submit
from authoring.views.write import Write
from authoring.views.media import MediaUpload, LoadEmbed
from authoring.views.new import New
from authoring.views.view import ViewAuthoredMaterial
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
    url(r"new$", New.as_view(), name="new"),
    url(r"edit/(?P<pk>\d+)$", Write.as_view(), name="write"),
    url(r"edit/(?P<pk>\d+)/upload$", MediaUpload.as_view(), name="upload"),
    url(r"edit/(?P<pk>\d+)/describe$", Describe.as_view(), name="describe"),
    url(r"edit/(?P<pk>\d+)/submit$", Submit.as_view(), name="submit"),
    url(r"load-embed$", LoadEmbed.as_view(), name="load-embed"),
    url(r"(?P<pk>\d+)$", ViewAuthoredMaterial.as_view(), name="view"),
)
