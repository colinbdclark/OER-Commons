from itertools import chain

from django.core.urlresolvers import reverse, resolve
from django.db.models.aggregates import Count
from django.template import Library
from django.contrib.contenttypes.models import ContentType

from materials.utils import get_name_from_slug
from materials.models import Material
from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from tags.models import Tag
from tags.tags_utils import get_tag_cloud
from saveditems.models import SavedItem
from myitems.models import Folder, FolderItem
from myitems.views import FolderForm, AllItems, SubmittedItems, PublishedItems, DraftItems

register = Library()

@register.inclusion_tag("myitems/include/my-tags-portlet.html", takes_context=True)
def my_tags_portlet(context):
    user = context["request"].user
    tags = dict(Tag.objects.filter(user=user).values("slug").annotate(count=Count("slug")).values_list("slug", "count"))
    tags = get_tag_cloud(tags, 3, 0, 1)
    for tag in tags:
        tag["name"] = get_name_from_slug(Tag, tag["slug"])
    return dict(tags=tags)


VIEWS = [
    AllItems,
    SubmittedItems,
    PublishedItems,
    DraftItems,
]


@register.inclusion_tag("myitems/include/views-portlet.html", takes_context=True)
def myitems_views_portlet(context):
    request = context["request"]
    current_path = request.path
    views = [
        {
            "url": reverse("myitems:%s" % view.slug),
            "title": view.name,
            "count": view.get_count(request.user),
            "name": view.slug,
        }
        for view in VIEWS
    ]
    folders = [
        {
            "url": f.get_absolute_url(),
            "title": f.name,
            "id": f.id,
            "count": f.folderitem__count,
        }
        for f in Folder.objects.filter(user=request.user).annotate(Count('folderitem'))
    ]

    for item in chain(views, folders):
        if item["url"] == current_path:
            item["selected"] = True
            break

    return {
        'views': views,
        'folders': folders,
        'folder_create_form': FolderForm(),
    }


@register.inclusion_tag("myitems/include/save-button.html", takes_context=True)
def myitems_save_button(context):
    request = context["request"]
    item = context["item"]
    content_type = ContentType.objects.get_for_model(item)

    if isinstance(item, Material):
        creator = item.creator
    elif isinstance(item, AuthoredMaterial):
        creator = item.author
    elif isinstance(item, AuthoredMaterialDraft):
        creator = item.material.author
    else:
        raise ValueError(u"Save button for '%s' is not supported." % type(item))

    saved = False
    folders = []
    if request.user.is_authenticated():
        saved = (creator == request.user) or SavedItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=item.id
        ).exists()
        saved_in_folders = set(FolderItem.objects.filter(
            content_type=content_type,
            object_id=item.id,
            folder__user=request.user,
        ).values_list("folder__id", flat=True))
        for f in Folder.objects.filter(user=request.user).annotate(Count('folderitem')):
            #noinspection PyUnresolvedReferences
            folders.append({
                "title": f.name,
                "id": f.id,
                "count": f.folderitem__count,
                "saved": f.id in saved_in_folders,
            })

    return {
        'folders': folders,
        'folder_create_form': FolderForm(),
        'saved': saved,
        'content_type': content_type.id,
        'object_id': item.id,
    }


PROFILE_TABS = [
    ("users", "profile", "Profile", None),
    ("myitems", "myitems", "My Items", None),
    ("preferences", "preferences", "", "preferences"),
]


@register.inclusion_tag("myitems/include/profile-tabs.html", takes_context=True)
def profile_tabs(context):
    request = context["request"]
    tabs = []
    for namespace, url_name, tab_name, tab_class in PROFILE_TABS:
        url = reverse("%s:%s" % (namespace, url_name))
        classes = []
        if resolve(request.path).namespace == namespace:
            classes.append("selected")
        if tab_class:
            classes.append(tab_class)

        tabs.append({
            'url': url,
            'name': tab_name,
            'classes': ' '.join(classes),
        })

    return {
        'tabs': tabs,
    }
