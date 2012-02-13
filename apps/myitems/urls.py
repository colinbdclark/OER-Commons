from django.conf.urls.defaults import patterns, url

from myitems.views import FolderCreate, FolderDelete


urlpatterns = patterns("myitems.views",
  url(r"^/?$", "saved", name="myitems"),
  url(r"^/rated/?$", "rated", name="rated"),
  url(r"^/tagged/?$", "tagged", name="tagged"),
  url(r"^/commented/?$", "commented", name="commented"),
  url(r"^/submitted/?$", "submitted", name="submitted"),
  url(r"^/searches/?$", "searches", name="searches"),
  url(r"^/folder-create/?$", FolderCreate.as_view(), name="folder_create"),
  url(r"^/folder/(?P<slug>.+)/?$", "folder", name="folder"),
  url(r"^/folder-delete/?$", FolderDelete.as_view(), name="folder_delete"),
)
