from __future__ import absolute_import

from django.conf import settings
from django.template.base import Library
from django.utils.safestring import mark_safe
from getsatisfaction.fastpass import FastPass


register = Library()


@register.simple_tag(takes_context=True)
def fastpass(context):
    user = context["request"].user
    key = getattr(settings, "GETSATISFACTION_KEY", None)
    secret = getattr(settings, "GETSATISFACTION_SECRET", None)
    if not key or not secret or not user.is_authenticated() or not user.email:
        return u""

    name = (u"%s %s" % (user.first_name, user.last_name)).strip() or user.username
    script = FastPass.script(key, secret, user.email, name, str(user.id))
    return mark_safe(script)
