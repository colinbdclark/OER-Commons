from django.core.urlresolvers import reverse, resolve
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.material import PUBLISHED_STATE
from materials.utils import get_name_from_slug
from materials.views.filters import FILTERS
from materials.views.index import PATH_FILTERS, BATCH_SIZE_OPTIONS, \
    SORT_BY_OPTIONS, serialize_query_string_params
from tags.models import Tag
from tags.utils import get_tag_cloud


def view_item(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    tags = {}
    for tag in item.tags.all():
        tags[tag.slug] = tags.get(tag.slug, 0) + 1
    tags = get_tag_cloud(tags, 3, 0, 1)
    for tag in tags:
        tag["name"] = get_name_from_slug(Tag, tag["slug"])

    user_tags = item.tags.filter(user=request.user)

    add_tags_url = None
    namespace = getattr(model, "namespace", None)
    if namespace:
        add_tags_url = reverse("materials:%s:add_tags" % namespace, kwargs=dict(slug=item.slug))


    came_from_index = False

    prev_item_url = u""
    next_item_url = u""
    index_url = u""
    hidden_filters = {}
    sort_by = u""
    batch_size = u""

    kwargs = {}
    index_path = request.REQUEST.get("index_path")
    if index_path:
        try:
            kwargs = resolve(index_path)[2]
            came_from_index = True
        except Http404:
            pass

    if came_from_index:

        query = SearchQuerySet().narrow("workflow_state:%s" % PUBLISHED_STATE)

        index_model = kwargs.get("model")

        if index_model:
            query = query.models(index_model)

        path_filter = None

        hidden_filters = {}
        query_string_params = {}
        search_query = u""

        for filter_name in PATH_FILTERS:
            value = kwargs.get(filter_name, None)
            if value is not None:
                filter = FILTERS[filter_name]
                query = filter.update_query(query, value)
                path_filter = filter_name
                break

        for filter_name, filter in FILTERS.items():
            if filter_name == path_filter:
                continue
            value = filter.extract_value(request)
            if value is not None:
                query = filter.update_query(query, value)
                hidden_filters[filter.request_name] = value
                query_string_params = filter.update_query_string_params(query_string_params, value)
                if filter_name == "search":
                    search_query = value

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

        if sort_by == "search":
            order_by = None
        elif sort_by == "date":
            order_by = "-published_on"
        else:
            order_by = "sortable_title"

        if order_by is not None:
            query = query.order_by(order_by)

        current_item_idx = 0
        for result in query:
            if result.model == model and int(result.pk) == item.id:
                if current_item_idx > 0:
                    prev_item = query[current_item_idx - 1]
                    namespace = getattr(prev_item.model, "namespace", None)
                    if namespace:
                        prev_item_url = reverse("materials:%s:view_item" % namespace, kwargs=dict(slug=prev_item.get_stored_fields()["slug"]))
                    else:
                        prev_item_url = result.object.get_absolute_url()

                if current_item_idx < (len(query) - 1):
                    next_item = query[current_item_idx + 1]
                    namespace = getattr(next_item.model, "namespace", None)
                    if namespace:
                        next_item_url = reverse("materials:%s:view_item" % namespace, kwargs=dict(slug=next_item.get_stored_fields()["slug"]))
                    else:
                        next_item_url = result.object.get_absolute_url()
                break
            current_item_idx += 1

        batch_start = (current_item_idx / batch_size) * batch_size
        if batch_start:
            query_string_params["batch_start"] = batch_start

        index_url = "%s?%s" % (index_path, serialize_query_string_params(query_string_params))

    return direct_to_template(request, "materials/view-item.html", locals())
