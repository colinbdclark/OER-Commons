from django.contrib.sites.models import Site
from django.template import Library
from django.template.defaultfilters import stringfilter


register = Library()


@register.filter
@stringfilter
def full_url(path):
    return "http://%s%s" % (Site.objects.get_current().domain, path)
full_url.is_safe = True
