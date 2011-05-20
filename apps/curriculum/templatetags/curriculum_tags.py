from curriculum.models import AlignmentTag
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Library


register = Library()


@register.inclusion_tag("curriculum/include/item-tags-portlet.html", takes_context=True)
def align_item_tags_portlet(context, item):

    item_tags = item.alignment_tags.all() 
    tag_ids = item_tags.values_list("tag", flat=True).order_by().distinct()
    tags = AlignmentTag.objects.filter(id__in=tag_ids)

    content_type = ContentType.objects.get_for_model(item)
    align_url = reverse("curriculum:align", args=(
                                    content_type.app_label,
                                    content_type.model,
                                    item.pk,
                                ))

    return dict(item=item, tags=tags, align_url=align_url)


@register.inclusion_tag("curriculum/include/align-form.html", takes_context=True)
def align_form(context):
    return dict()