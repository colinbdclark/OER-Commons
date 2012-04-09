from itertools import chain

from django.core.urlresolvers import reverse, resolve
from django.db.models.aggregates import Count
from django.template import Library
from materials.utils import get_name_from_slug
from tags.models import Tag
from tags.tags_utils import get_tag_cloud

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
    content_type = context["content_type"]
    folders = ((
            {
                "url": f.get_absolute_url(),
                "title": f.name,
                "id": f.id,
                "count": f.folderitem__count,
                "saved": FolderItem.objects.filter(
                    folder=f, content_type=content_type, object_id=item.id).exists()
            }
            for f in Folder.objects.filter(user=request.user).annotate(Count('folderitem'))
        ) if request.user.is_authenticated()
        else []
    )
    return {
        'folders': folders,
        'folder_create_form': FolderForm(),
        'saved': context["saved"],
        'save_url': context["save_url"],
        'unsave_url': context["unsave_url"],
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
