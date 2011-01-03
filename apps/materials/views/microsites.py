from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models import Microsite
from materials.models.common import Keyword
from materials.models.material import PUBLISHED_STATE
from materials.utils import get_name_from_slug
from materials.views.index import populate_item_from_search_result, \
    MAX_TOP_KEYWORDS
from tags.models import Tag
from tags.tags_utils import get_tag_cloud


def microsite(request, microsite):

    microsite = get_object_or_404(Microsite, slug=microsite)

    page_title = u"%s Home" % microsite.name
    breadcrumbs = [{"url": reverse("materials:microsite", kwargs=dict(microsite=microsite.slug)), "title": page_title}]

    query = SearchQuerySet().narrow("workflow_state:%s" % PUBLISHED_STATE)
    query = query.narrow("microsites:%i" % microsite.id)
    query = query.order_by("-rating")
    query = query.facet("topics").facet("keywords").facet("grade_levels").facet("course_material_types")

    items = []
    results = query[0:8]
    for result in results:
        items.append(populate_item_from_search_result(result))

    facets = query.facet_counts()["fields"]

    keywords = facets.get("keywords", [])
    if len(keywords) > MAX_TOP_KEYWORDS:
        keywords = keywords[:MAX_TOP_KEYWORDS]
    keywords = get_tag_cloud(dict(keywords), 3, 0, 0)
    for keyword in keywords:
        name = get_name_from_slug(Keyword, keyword["slug"]) or \
               get_name_from_slug(Tag, keyword["slug"]) or \
               keyword["slug"]
        keyword["name"] = name

    return direct_to_template(request, "materials/microsites/%s.html" % microsite.slug, locals())
