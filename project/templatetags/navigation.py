from django.template import Library
from django.core.urlresolvers import reverse


register = Library()


@register.inclusion_tag("include/navigation.html", takes_context=True)
def navigation(context):
    request = context["request"]
    path_elements = [el for el in request.path.split("/") if el]
    tabs = []
    microsite = getattr(request, "microsite", None)

    tab = {}
    tab["title"] = u"Browse All"
    if microsite:
        tab["url"] = reverse("materials:browse", kwargs={"microsite": microsite})
        tab["selected"] = len(path_elements) > 1 and path_elements[1] in \
            ['oer', 'browse', 'courses', 'libraries', 'advanced_search', 'search']
    else:
        tab["url"] = reverse("materials:browse")
        tab["selected"] = path_elements and path_elements[0] in \
            ['oer', 'browse', 'courses', 'libraries', 'advanced_search', 'search']
    tabs.append(tab)

    tab = {}
    tab["title"] = u"OER Landscape"
    tab["url"] = reverse("materials:community")
    tab["selected"] = path_elements and path_elements[0] == "community"
    tabs.append(tab)

    tab = {}
    tab["title"] = u"My Items"
    tab["url"] = reverse("user_items")
    tab["selected"] = path_elements and path_elements[0] == "my"
    tabs.append(tab)

    return dict(tabs=tabs)
