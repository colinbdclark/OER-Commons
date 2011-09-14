from common.models import Keyword
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import fix_ampersands
from django.utils.safestring import mark_safe
from materials.models.common import COU_BUCKETS, License


register = Library()


def shrink(value, arg=None):
    """
    Reduce the length of given string. Replace ' and ' word with ampersand,
    cut the string if it's longer than given length.
    """
    if arg is None:
        length = 50
    else:
        try:
            length = int(arg)
        except ValueError:
            return u""
    value = value.replace(u" and ", u" & ")
    if len(value) > length:
        value = value[:length] + u"&hellip;"
    return mark_safe(fix_ampersands(value));
shrink.is_safe = True
register.filter(stringfilter(shrink))


@register.inclusion_tag("materials/include/hidden-filters.html")
def hidden_filters(hidden_filters):
    filters = []
    for name, value in hidden_filters.items():
        if isinstance(value, basestring):
            filters.append(dict(name=name, value=value))
        elif isinstance(value, list):
            for v in value:
                filters.append(dict(name=name, value=v))
        elif isinstance(value, bool):
            filters.append(dict(name=name, value=value and "yes" or "no"))
    return dict(filters=filters)


@register.inclusion_tag("materials/include/cou-bucket.html")
def cou_bucket(bucket=None):
    if not bucket:
        return {}
    buckets = dict(COU_BUCKETS)
    if bucket not in buckets:
        return {}
    return dict(slug=bucket, title=buckets[bucket])


@register.inclusion_tag("materials/forms/include/suggested-keywords-options.html")
def suggested_keywords_options():
    return dict(keywords=Keyword.objects.filter(suggested=True).order_by("name").values_list("name", flat=True))


@register.simple_tag
def get_cc_license_name(url):
    return License.objects.get_cc_license_name_from_url(url)


@register.inclusion_tag("materials/forms/include/cc-selection-widget.html", takes_context=True)
def cc_selection_widget(context):
    return dict(fields=License.objects.get_cc_issue_fields(),
                STATIC_URL=context["STATIC_URL"])
