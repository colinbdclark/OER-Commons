from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import fix_ampersands
from django.utils.safestring import mark_safe


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
shrink = stringfilter(shrink)


register.filter(shrink)

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
    return locals()
