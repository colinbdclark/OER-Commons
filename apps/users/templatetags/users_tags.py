from django.template import Library


register = Library()


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
    