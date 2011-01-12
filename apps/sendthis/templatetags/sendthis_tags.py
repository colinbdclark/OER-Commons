from django.template import Library
from sendthis.views import SendThisForm


register = Library()


@register.inclusion_tag("sendthis/include/form.html", takes_context=True)
def send_this_form(context, path):
    form = SendThisForm()
    return dict(form=form, path=path, request=context["request"])
