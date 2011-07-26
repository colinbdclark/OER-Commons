from django.core.urlresolvers import reverse
from django.template import Library


register = Library()


VIEWS = [
    ("users:profile_edit", u"Basic Information and Password"),
    ("users:profile_geography", u"Location"),
    ("users:profile_roles", u"Role"),
    ("users:profile_about", u"About Me"),
    ("preferences:preferences", u"Settings"),
]


@register.inclusion_tag("users/include/profile-views.html", takes_context=True)
def profile_views(context):
    request = context["request"]
    views = []
    for view_name, title in VIEWS:
        url = reverse(view_name)
        views.append(dict(title=title, url=url,
                          selected=request.path == url))
    return dict(views=views)


PROFILE_NOTIFICATION_HIDE_COOKIE_NAME = "_hpn"


@register.inclusion_tag("users/include/profile-notification.html", takes_context=True)
def profile_notification(context, notification_class):
    request = context["request"]
    user = request.user
    
    if not user.is_authenticated():
        return
    
    profile = user.get_profile()
    total_fields = profile.total_fields
    
    cookie = request.COOKIES.get(PROFILE_NOTIFICATION_HIDE_COOKIE_NAME)
    if cookie and int(cookie) == total_fields:
        return

    completeness = profile.completeness
    if completeness == 100:
        return
    
    return dict(completeness=completeness, total_fields=total_fields,
                cookie_name=PROFILE_NOTIFICATION_HIDE_COOKIE_NAME,
                notification_class=notification_class)
    
