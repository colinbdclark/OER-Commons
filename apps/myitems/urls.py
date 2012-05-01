from django.conf.urls.defaults import patterns, url
from django_js_utils.core import expose_to_js

from myitems.views import FolderCreate, FolderDelete, FolderAddItem
from myitems.views import FolderItemDelete, ItemDelete
from myitems.views import AllItems, SubmittedItems, PublishedItems, DraftItems, FolderItems


urlpatterns = patterns("myitems.views",
  url(r"^$", AllItems.as_view(), name="myitems"),
  url(r"^/submitted$", SubmittedItems.as_view(), name="submitted"),
  url(r"^/published$", PublishedItems.as_view(), name="published"),
  url(r"^/draft$", DraftItems.as_view(), name="draft"),
  url(r"^/folder-create$", FolderCreate.as_view(), name="folder_create"),
  expose_to_js(url(r"^/folder/(?P<slug>.+)$", FolderItems.as_view(), name="folder")),
  expose_to_js(url(r"^/folder-delete$", FolderDelete.as_view(), name="folder_delete")),
  expose_to_js(url(r"^/folder-add-item$", FolderAddItem.as_view(), name="folder_add_item")),
  expose_to_js(url(r"^/folder-delete-item$", FolderItemDelete.as_view(), name="folder_delete_item")),
  expose_to_js(url(r"^/delete-item$", ItemDelete.as_view(), name="delete_item")),
)
