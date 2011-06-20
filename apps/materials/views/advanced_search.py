from django.views.generic.simple import direct_to_template
from materials.views.filters import FILTERS, VocabularyFilter, ChoicesFilter
from django.core.urlresolvers import reverse
from materials.models.common import LICENSE_HIERARCHY, LICENSE_TYPES


ADVANCED_SEARCH_FILTERS = (
   ("general_subjects", False),
   ("grade_levels", False),
   ("cou_bucket", False),
   ("languages", False),
   ("course_material_types", False),
   ("course_or_module", False),
   ("media_formats", False),
   ("member_activities", False),
   ("library_material_types", False),
   ("community_types", True),
   ("community_topics", True),
   ("cou_bucket", False),
)


def advanced_search(request):

    filters = {}

    for filter_name, collapsed in ADVANCED_SEARCH_FILTERS:
        filter = FILTERS[filter_name]
        filter_data = {"name": filter_name,
                       "title": filter.title,
                       "options": [],
                       "request_name": filter.request_name,
                       "collapsed": collapsed}
        if isinstance(filter, VocabularyFilter):
            for option in filter.model.objects.values("id", "slug", "name"):
                option["input_id"] = "%s-%i" % \
                                (filter_data["request_name"].replace(".", "-"),
                                 option["id"])
                filter_data["options"].append(option)
        elif isinstance(filter, ChoicesFilter):
            for i, (slug, name) in enumerate(filter.choices):
                option = {"id": i, "slug": slug, "name": name}
                option["input_id"] = "%s-%i" % \
                                (filter_data["request_name"].replace(".", "-"),
                                 option["id"])
                filter_data["options"].append(option)
        filters[filter_name] = filter_data

    license_types_dict = dict(LICENSE_TYPES)
    license_hierarchy_dict = dict(LICENSE_HIERARCHY)
    filters["cou_bucket"]["sub_option_request_name"] = FILTERS["license_type"].request_name
    for option in filters["cou_bucket"]["options"]:
        option["options"] = []
        for i, license_type in enumerate(license_hierarchy_dict[option["slug"]]):
            sub_option = {"id": i,
                          "slug": license_type,
                          "name": license_types_dict[license_type]}
            sub_option["input_id"] = "%s-%i%i" % \
                                (filters["cou_bucket"]["sub_option_request_name"].replace(".", "-"),
                                 option["id"], sub_option["id"])
            option["options"].append(sub_option)

    page_title = u"Advanced Search"
    breadcrumbs = [{"url": reverse("materials:advanced_search"),
                    "title": page_title}]

    return direct_to_template(request, "materials/advanced-search.html",
                              locals())
