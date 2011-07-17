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

