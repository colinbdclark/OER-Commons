from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.template import Library
from materials.utils import get_name_from_slug
from tags.models import Tag
from tags.tags_utils import get_tag_cloud


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
    ("myitems", u"My Saved Items"),
    ("rated", u"My Rated Items"),
    ("tagged", u"My Tagged Items"),
    ("commented", u"My Commented Items"),
    ("submitted", u"My Submitted Items"),
    ("searches", u"My Saved Searches"),
]


@register.inclusion_tag("myitems/include/views-portlet.html", takes_context=True)
def myitems_views_portlet(context):
    current_path = context["request"].path
    views = []
    for view_name, view_title in VIEWS:
        url = reverse("myitems:%s" % view_name)
        views.append({
            "url": url,
            "title": view_title,
            "selected": url == current_path,
        })

    for f in context["folders"]:
        url = reverse("myitems:folder", kwargs={"slug": f.slug})
        views.append({
            "url": url,
            "title": f.name,
            "selected": url == current_path,
        })

    return dict(views=views, form=context["folder_create_form"])
