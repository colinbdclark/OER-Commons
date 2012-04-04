from itertools import chain

from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.template import Library
from materials.utils import get_name_from_slug
from tags.models import Tag
from tags.tags_utils import get_tag_cloud

from myitems.models import Folder
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

    return dict(views=views, folders=folders, folder_create_form=FolderForm())
