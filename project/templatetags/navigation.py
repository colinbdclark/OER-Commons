from django.template import Library
from django.core.urlresolvers import reverse, resolve, Resolver404


register = Library()


@register.inclusion_tag("include/navigation.html", takes_context=True)
def navigation(context):
    request = context["request"]
    path_elements = [el for el in request.path.split("/") if el]
    tabs = []
    microsite = getattr(request, "microsite", None)
    try:
        view_name = resolve(request.path).view_name
    except Resolver404:
        view_name = ""

    tabs.append(dict(
        title=u"Home",
        url=reverse("frontpage"),
        selected=view_name == "frontpage"
    ))

    tab = dict(title=u"Browse All")
    if microsite:
        tab["url"] = reverse("materials:browse", kwargs={"microsite": microsite})
        tab["selected"] = len(path_elements) > 1 and path_elements[1] in \
            ['oer', 'browse', 'courses', 'libraries', 'advanced_search', 'search']
    else:
        tab["url"] = reverse("materials:browse")
        tab["selected"] = path_elements and path_elements[0] in \
            ['oer', 'browse', 'courses', 'libraries', 'advanced_search', 'search']
    tabs.append(tab)

    tab = dict(title=u"My OER")
    tab["url"] = reverse("myitems:myitems")
    tab["selected"] = view_name.startswith("myitems:") or view_name.startswith("users:profile")
    tab["class"] = "require-login"
    tabs.append(tab)

    tabs.append(dict(
        title=u"Contribute",
        url=reverse("contribute"),
        selected=view_name == "contribute"
    ))

    return dict(tabs=tabs)
