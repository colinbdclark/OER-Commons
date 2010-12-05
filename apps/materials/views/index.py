from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.common import GeneralSubject, GradeLevel, Collection, \
    Keyword
from materials.models.community import CommunityItem
from materials.models.material import PUBLISHED_STATE
from materials.utils import get_name_from_id, get_slug_from_id, \
    first_neighbours_last, get_name_from_slug
from materials.views.filters import FILTERS, VocabularyFilter, ChoicesFilter
from tags.utils import get_tag_cloud
import urllib
from tags.models import Tag



BATCH_SIZE_OPTIONS = (
    10, 20, 50, 100
)

SORT_BY_OPTIONS = (
    {"value": u"title", "title": u"Title"},
    {"value": u"search", "title": u"Relevance"},
    {"value": u"rating", "title": u"Rating"},
    {"value": u"date", "title": u"Date"},
    {"value": u"visits", "title": u"Visits"},
)

MAX_TOP_KEYWORDS = 25


def serialize_query_string_params(query_string_params):
    params = []
    for key, value in query_string_params.items():
        if isinstance(value, list):
            for v in value:
                if isinstance(v, unicode):
                    v = v.encode("utf-8")
                params.append((key, v))
        else:
            if isinstance(value, unicode):
                value = value.encode("utf-8")
            params.append((key, value))
    params.sort()
    return urllib.urlencode(params)


def build_pagination(path, query_string_params, batch_start, batch_size, total_items):
    pagination = dict(first_page_url=None,
                 last_page_url=None,
                 next_page_url=None,
                 prev_page_url=None,
                 pages=[])

    if not total_items:
        return pagination

    total_pages = total_items / batch_size
    if total_items % batch_size:
        total_pages += 1
    current_page = batch_start / batch_size

    if current_page != 0:
        params = query_string_params.copy()
        params["batch_start"] = 0
        pagination["first_page_url"] = path + "?" + serialize_query_string_params(params)

        params = query_string_params.copy()
        params["batch_start"] = (current_page - 1) * batch_size
        pagination["prev_page_url"] = path + "?" + serialize_query_string_params(params)

    if current_page < (total_pages - 1):
        params = query_string_params.copy()
        params["batch_start"] = (total_pages - 1) * batch_size
        pagination["last_page_url"] = path + "?" + serialize_query_string_params(params)

        params = query_string_params.copy()
        params["batch_start"] = (current_page + 1) * batch_size
        pagination["next_page_url"] = path + "?" + serialize_query_string_params(params)

    for page in first_neighbours_last(xrange(total_pages), current_page, 3, 3):
        if page is None:
            pass
        elif page == current_page:
            page = dict(number=page + 1, url=None)
        else:
            params = query_string_params.copy()
            params["batch_start"] = page * batch_size
            url = path + "?" + serialize_query_string_params(params)
            page = dict(number=page + 1, url=url)
        pagination["pages"].append(page)

    return pagination


BASIC_INDEX_FILTERS = (
  ("general_subjects", False,),
  ("grade_levels", False,),
  ("course_material_types", True,),
  ("media_formats", True,),
  (u"cou_bucket", True),
)


def build_index_filters(visible_filters, facets, filter_values, path_filter):
    filters = {}
    for filter_name, collapsed in BASIC_INDEX_FILTERS:
        if filter_name not in visible_filters:
            continue
        filter = FILTERS[filter_name]
        if not facets.get(filter_name):
            continue
        counts = dict(facets[filter_name])
        values = filter_values.get(filter_name, [])
        filter_data = {}
        filter_data["name"] = filter_name
        filter_data["title"] = filter.title
        filter_data["disabled"] = filter_name == path_filter
        filter_data["options"] = []
        filter_data["all_checked"] = not bool(values)
        filter_data["request_name"] = filter.request_name
        filter_data["collapsed"] = collapsed
        if values:
            filter_data["collapsed"] = False
        if isinstance(filter, VocabularyFilter):
            if not isinstance(values, list):
                values = [values]
            for option in filter.model.objects.values("id", "slug", "name"):
                count = counts.get(str(option["id"]), 0)
                option["count"] = count
                if filter_data["all_checked"] or option["slug"] in values:
                    option["checked"] = True
                option["input_id"] = "%s-%i" % (filter_data["request_name"].replace(".", "-"), option["id"])
                filter_data["options"].append(option)
        elif isinstance(filter, ChoicesFilter):
            if not isinstance(values, list):
                values = [values]
            for i, (slug, name) in enumerate(filter.choices):
                option = {}
                option["id"] = i
                option["slug"] = slug
                option["name"] = name
                count = counts.get(slug, 0)
                option["count"] = count
                if filter_data["all_checked"] or slug in values:
                    option["checked"] = True
                option["input_id"] = "%s-%i" % (filter_data["request_name"].replace(".", "-"), option["id"])
                filter_data["options"].append(option)
        if len(filter_data["options"]) == len(values):
            filter_data["all_checked"] = True
        filters[filter_name] = filter_data

    return filters


PATH_FILTERS = ["general_subjects", "grade_levels", "course_material_types",
                "library_material_types", "collection", "keywords", "license",
                "ocw", "course_or_module", "community_types",
                "community_topics"]


def index(request, general_subjects=None, grade_levels=None,
          course_material_types=None, library_material_types=None,
          collection=None, keywords=None, license=None, ocw=None,
          course_or_module=None, community_types=None, community_topics=None,
          microsite=None, model=None, search=False,
          facet_fields=["general_subjects", "grade_levels", "keywords",
                        "course_material_types", "media_formats",
                        "cou_bucket"]):

    query_string_params = {}
    filter_values = {}
    page_title = u"Browse"
    page_subtitle = u""
    breadcrumbs = [{"url": reverse("materials:browse"), "title": u"OER Materials"}]

    query = SearchQuerySet().narrow("workflow_state:%s" % PUBLISHED_STATE)

    if model:
        query = query.models(model)

    path_filter = None

    visible_filters = ["search", "general_subjects", "grade_levels",
                       "course_material_types", "media_formats",
                       "cou_bucket"]
    hidden_filters = {}

    for filter_name in PATH_FILTERS:
        value = locals()[filter_name]
        if value is not None:
            filter = FILTERS[filter_name]
            query = filter.update_query(query, value)
            path_filter = filter_name
            page_subtitle = filter.page_subtitle(value)
            filter_values[filter_name] = value
            break

    search_query = u""

    for filter_name, filter in FILTERS.items():
        if filter_name == path_filter:
            continue
        value = filter.extract_value(request)
        if value is not None:
            query = filter.update_query(query, value)
            query_string_params = filter.update_query_string_params(query_string_params, value)
            filter_values[filter_name] = value
            if filter_name not in visible_filters:
                hidden_filters[filter.request_name] = value
            if filter_name == "search":
                search_query = value

    if search:
        page_title = "Search"
        page_subtitle = search_query
        breadcrumbs = [{"url": reverse("materials:search"), "title": u"Search"}]

    elif model == CommunityItem:
        breadcrumbs = [{"url": reverse("materials:community"), "title": u"OER Community"}]

    if microsite:
        breadcrumbs = [{"url": reverse("microsite", kwargs=dict(microsite=microsite)), "title": microsite}] + breadcrumbs

    if not page_subtitle and model:
        page_subtitle = u"Content Type: %s" % model._meta.verbose_name_plural

    try:
        batch_start = int(request.REQUEST.get("batch_start", 0))
    except:
        batch_start = 0
    query_string_params["batch_start"] = batch_start

    batch_size_options = BATCH_SIZE_OPTIONS

    try:
        batch_size = int(request.REQUEST.get("batch_size", 0))
    except:
        batch_size = 20
    if batch_size not in batch_size_options:
        batch_size = 20
    query_string_params["batch_size"] = batch_size

    sort_by_options = SORT_BY_OPTIONS

    sort_by = request.REQUEST.get("sort_by", request.REQUEST.get("sort_on"))
    if not sort_by or sort_by not in [o["value"] for o in sort_by_options]:
        if sort_by == "publication_time":
            sort_by = "date"
        elif sort_by == "overall_rating":
            sort_by = "rating"
        elif search_query:
            sort_by = "search"
        else:
            sort_by = "title"
    query_string_params["sort_by"] = sort_by

    for facet_field in facet_fields:
        query = query.facet(facet_field)

    batch_end = batch_start + batch_size

    if sort_by == "search":
        order_by = None
    elif sort_by == "date":
        order_by = "-published_on"
    else:
        order_by = "sortable_title"

    if order_by is not None:
        query = query.order_by(order_by)

    results = query[batch_start:batch_end]
    items = []
    for result in results:
        item = result.get_stored_fields()
        if item.get("collection"):
            collection_id = item["collection"]
            item["collection"] = {"name": get_name_from_id(Collection,
                                                           collection_id),
                                  "slug": get_slug_from_id(Collection,
                                                           collection_id)}
        if item.get("general_subjects"):
            item["general_subjects"] = [get_name_from_id(GeneralSubject, id) for id in item["general_subjects"]]

        if item.get("grade_levels"):
            item["grade_levels"] = [get_name_from_id(GradeLevel, id) for id in item["grade_levels"]]

        namespace = getattr(result.model, "namespace", None)
        if namespace:
            item["get_absolute_url"] = reverse("materials:%s:view_item" % namespace, kwargs=dict(slug=item["slug"]))
        else:
            item["get_absolute_url"] = result.object.get_absolute_url()

        items.append(item)

    total_items = len(query)

    first_item_number = batch_start + 1
    last_item_number = batch_start + batch_size
    if last_item_number > total_items:
        last_item_number = total_items

    pagination = build_pagination(request.path, query_string_params,
                                  batch_start, batch_size, total_items)

    facets = query.facet_counts()["fields"]

    index_filters = build_index_filters(visible_filters,
                                        facets,
                                        filter_values, path_filter)

    all_keywords = facets.get("keywords", [])
    if len(all_keywords) > MAX_TOP_KEYWORDS:
        top_keywords = get_tag_cloud(dict(all_keywords[:MAX_TOP_KEYWORDS]), 3, 0, 0)
        all_keywords = get_tag_cloud(dict(all_keywords), 3, 0, 0)
    else:
        top_keywords = get_tag_cloud(dict(all_keywords), 3, 0, 0)
        all_keywords = []

    for keyword in top_keywords:
        name = get_name_from_slug(Keyword, keyword["slug"]) or \
               get_name_from_slug(Tag, keyword["slug"]) or \
               keyword["slug"]
        keyword["name"] = name
    for keyword in all_keywords:
        name = get_name_from_slug(Keyword, keyword["slug"]) or \
               get_name_from_slug(Tag, keyword["slug"]) or \
               keyword["slug"]
        keyword["name"] = name

    return direct_to_template(request, "materials/index.html", locals())
