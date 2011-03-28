from django.contrib.contenttypes.models import ContentType
from django.template import Library
from materials.utils import get_name_from_slug
from tags.models import Tag
from tags.tags_utils import get_tag_cloud


register = Library()


@register.inclusion_tag("tags/include/item-tags-portlet.html", takes_context=True)
def item_tags_portlet(context, item):
    request = context["request"]
    user = request.user
    if user.is_authenticated():
        user_tags = item.tags.filter(user=user).order_by("slug")
        can_add_tags = True
    else:
        user_tags = []
        can_add_tags = False

    item_tags = item.tags.all() 
    if user_tags:
        item_tags = item_tags.exclude(id__in=user_tags.values_list("id", flat=True))

    tags = {}
    for tag in item_tags:
        tags[tag.slug] = tags.get(tag.slug, 0) + 1
    tags = get_tag_cloud(tags, 3, 0, 1)
    for tag in tags:
        tag["name"] = get_name_from_slug(Tag, tag["slug"])

    content_type = ContentType.objects.get_for_model(item)

    return dict(item=item,
                tags=tags,
                user_tags=user_tags,
                app_label=content_type.app_label,
                model=content_type.model,
                can_add_tags=can_add_tags)


@register.inclusion_tag("tags/include/add-tags-form.html", takes_context=True)
def add_tags_form(context):        
    request = context["request"]
    can_add_tags = request.user.is_authenticated()
    return dict(can_add_tags=can_add_tags)