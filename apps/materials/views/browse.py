from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.common import GeneralSubject, GradeLevel, Collection
from materials.models.course import COURSE_OR_MODULE, CourseMaterialType, \
    Course
from materials.models.library import LibraryMaterialType, Library
from materials.models.material import PUBLISHED_STATE
from materials.utils import get_facets_for_field
from materials.models.community import CommunityTopic, CommunityType


def browse(request, microsite=None):

    general_subjects_facets = dict(get_facets_for_field("general_subjects"))
    general_subjects = list(GeneralSubject.objects.values("id", "slug", "name"))
    for o in general_subjects:
        o["count"] = general_subjects_facets.get(unicode(o["id"]), 0)


    grade_levels_facets = dict(get_facets_for_field("grade_levels"))
    grade_levels = list(GradeLevel.objects.values("id", "slug", "name"))
    for o in grade_levels:
        o["count"] = grade_levels_facets.get(unicode(o["id"]), 0)

    course_material_types_facets = dict(get_facets_for_field("course_material_types"))
    course_material_types = list(CourseMaterialType.objects.values("id", "slug", "name"))
    course_material_types_col1 = []
    course_material_types_col2 = []
    for i, o in enumerate(course_material_types):
        o["count"] = course_material_types_facets.get(unicode(o["id"]), 0)
        if i < (len(course_material_types) / 2 + len(course_material_types) % 2):
            course_material_types_col1.append(o)
        else:
            course_material_types_col2.append(o)

    library_material_types_facets = dict(get_facets_for_field("library_material_types"))
    library_material_types = list(LibraryMaterialType.objects.values("id", "slug", "name"))
    for o in library_material_types:
        o["count"] = library_material_types_facets.get(unicode(o["id"]), 0)

    course_or_module_facets = dict(get_facets_for_field("course_or_module"))
    course_or_module = [dict(slug=slug, name=name) for slug, name in COURSE_OR_MODULE]
    for o in course_or_module:
        o["count"] = course_or_module_facets.get(unicode(o["slug"]), 0)

    ocw_count = len(SearchQuerySet().narrow("workflow_state:%s" % PUBLISHED_STATE).narrow("ocw:true"))

    page_title = u"Browse OER Materials"
    breadcrumbs = [{"url": reverse("materials:browse"), "title": u"OER Materials"}]

    return direct_to_template(request, "materials/browse.html", locals())


def providers(request, microsite=None):

    course_collections_facets = dict(get_facets_for_field("collection", Course))
    course_collections = list(Collection.objects.order_by("slug").values("id", "slug", "name"))
    for o in course_collections:
        o["count"] = course_collections_facets.get(unicode(o["id"]), 0)
    course_collections = [o for o in course_collections if o["count"]]

    library_collections_facets = dict(get_facets_for_field("collection", Library))
    library_collections = list(Collection.objects.order_by("slug").values("id", "slug", "name"))
    for o in library_collections:
        o["count"] = library_collections_facets.get(unicode(o["id"]), 0)
    library_collections = [o for o in library_collections if o["count"]]

    page_title = u"Browse Collection Providers"
    breadcrumbs = [{"url": reverse("materials:browse"), "title": u"OER Materials"}]

    return direct_to_template(request, "materials/browse-providers.html", locals())


def community(request):

    community_topics_facets = dict(get_facets_for_field("community_topics"))
    community_topics = list(CommunityTopic.objects.values("id", "slug", "name"))
    for o in community_topics:
        o["count"] = community_topics_facets.get(unicode(o["id"]), 0)

    community_types_facets = dict(get_facets_for_field("community_types"))
    community_types = list(CommunityType.objects.values("id", "slug", "name"))
    for o in community_types:
        o["count"] = community_types_facets.get(unicode(o["id"]), 0)
    community_types = [o for o in community_types if o["count"]]

    page_title = u"OER Community"
    breadcrumbs = [{"url": reverse("materials:community"), "title": u"OER Community"}]

    return direct_to_template(request, "materials/community.html", locals())
