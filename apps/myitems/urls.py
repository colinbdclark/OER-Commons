from django.conf.urls.defaults import patterns, url
from django_js_utils.core import expose_to_js

from myitems.views import FolderCreate, FolderDelete, FolderAddItem
from myitems.views import FolderItemDelete, ItemDelete


urlpatterns = patterns("myitems.views",
  url(r"^$", "myitems", name="myitems"),
  url(r"^/submitted$", "submitted", name="submitted"),
  url(r"^/searches$", "searches", name="searches"),
  url(r"^/folder-create$", FolderCreate.as_view(), name="folder_create"),
  expose_to_js(url(r"^/folder/(?P<slug>.+)$", "folder", name="folder")),
  expose_to_js(url(r"^/folder-delete$", FolderDelete.as_view(), name="folder_delete")),
  expose_to_js(url(r"^/folder-add-item$", FolderAddItem.as_view(), name="folder_add_item")),
  expose_to_js(url(r"^/folder-delete-item$", FolderItemDelete.as_view(), name="folder_delete_item")),
  expose_to_js(url(r"^/delete-item$", ItemDelete.as_view(), name="delete_item")),
)
