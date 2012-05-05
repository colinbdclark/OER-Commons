from itertools import chain

from django.core.urlresolvers import reverse, resolve
from django.db.models.aggregates import Count
from django.template import Library
from django.contrib.contenttypes.models import ContentType

from materials.models import Material
from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from saveditems.models import SavedItem
from myitems.models import Folder, FolderItem
from myitems.views import FolderForm, AllItems, SubmittedItems, PublishedItems, DraftItems

register = Library()


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
    else:
        raise ValueError(u"Save button for '%s' is not supported." % type(item))

    created = False
    saved = False
    auto_folder = None
    folders = []
    if request.user.is_authenticated():
        if creator == request.user:
            created = True
            auto_folder = "Submitted" if isinstance(item, Material) else "Published"
        else:
            saved = SavedItem.objects.filter(
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

    folder_number = len(saved_in_folders)+(auto_folder is not None)

    return {
        'folders': folders,
        'folder_create_form': FolderForm(),
        'saved': saved,
        'created': created,
        'content_type': content_type.id,
        'object_id': item.id,
        'auto_folder': auto_folder,
        'folder_number': folder_number,
        'folder_list_label': (
            "Select a folder" if folder_number == 0
            else (
                    auto_folder or (f["title"] for f in folders if f["saved"]).next() if folder_number == 1
                    else "%d folders" % folder_number
            )
        ),
    }


PROFILE_TABS = [
    ("users", "profile", "Profile", None),
    ("myitems", "myitems", "My Items", None),
    ("users", "profile_preferences", "", "preferences"),
]


@register.inclusion_tag("myitems/include/profile-tabs.html", takes_context=True)
def profile_tabs(context):
    request = context["request"]
    tabs = []
    match = resolve(request.path)
    for namespace, url_name, tab_name, tab_class in PROFILE_TABS:
        url = reverse("%s:%s" % (namespace, url_name))
        classes = []
        if match.namespace == namespace and (namespace != "users" or
            (match.url_name == url_name if url_name == "profile_preferences" else
            match.url_name != "profile_preferences")):
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
