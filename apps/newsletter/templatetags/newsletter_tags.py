from django.conf import settings
from django.template import Library
from newsletter.views import SubscribeForm


register = Library()


@register.inclusion_tag("newsletter/portlet.html", takes_context=True)
def newsletter_portlet(context):
    
    api_key = getattr(settings, "MAILCHIMP_API_KEY", None)
    list_id = getattr(settings, "MAILCHIMP_LIST_ID", None)
    
    if not api_key or not list_id:
        return dict()
    
    request = context["request"]

    initial = {}
    if request.user.is_authenticated():
        initial["email"] = request.user.email
        
    form = SubscribeForm(initial=initial) 
    
    return dict(form=form)