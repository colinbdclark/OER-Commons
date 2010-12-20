from django.conf import settings
from django.contrib.sites.models import Site
from django.forms.fields import FileField
from django.template import Library
from django.template.defaultfilters import stringfilter


register = Library()


@register.filter
@stringfilter
def full_url(path):
    return "http://%s%s" % (Site.objects.get_current().domain, path)
full_url.is_safe = True


@register.inclusion_tag("utils/include/next-url-input.html",
                        takes_context=True)
def next_url_input(context):
    request = context["request"]
    field_name = settings.REDIRECT_FIELD_NAME
    next_url = request.REQUEST.get(field_name, u"")
    return dict(field_name=field_name, next_url=next_url)


@register.filter
def bound_field_value(field):
    if not field.form.is_bound:
        data = field.form.initial.get(field.name, field.field.initial)
        if callable(data):
            data = data()
    else:
        if isinstance(field.field, FileField) and field.data is None:
            data = field.form.initial.get(field.name, field.field.initial)
        else:
            data = field.data
    return data
