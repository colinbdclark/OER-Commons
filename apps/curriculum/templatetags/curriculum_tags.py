from curriculum.models import AlignmentTag, TaggedMaterial
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Library


register = Library()


@register.inclusion_tag("curriculum/include/item-tags-portlet.html", takes_context=True)
def align_item_tags_portlet(context, item):

    user = context["request"].user
    content_type = ContentType.objects.get_for_model(item)

    user_tags = []
    if user.is_authenticated():
        for tagged in TaggedMaterial.objects.filter(content_type=content_type,
                                                    object_id=item.id,
                                                    user=user).select_related():
            user_tags.append(tagged)

    item_tags = item.alignment_tags.all()
    tag_ids = set(item_tags.values_list("tag", flat=True).order_by().distinct())
    tag_ids = tag_ids - set([tagged.tag.id for tagged in user_tags])
    tags = AlignmentTag.objects.filter(id__in=tag_ids)

    return dict(item=item, tags=tags, user_tags=user_tags)


@register.inclusion_tag("curriculum/include/align-form.html", takes_context=True)
def align_form(context, item=None):
    action = ""
    if item:
        content_type = ContentType.objects.get_for_model(item)
        action = reverse("curriculum:align",
                         args=(content_type.app_label,
                               content_type.model,
                               item.pk,
                        ))
    return dict(action=action)