from curriculum.utils import get_item_tags
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Library


register = Library()


@register.inclusion_tag("curriculum/include/item-tags-portlet.html", takes_context=True)
def align_item_tags_portlet(context, item):
    user = context["request"].user
    data = {"tags": get_item_tags(item, user), "item": item}
    return data


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
