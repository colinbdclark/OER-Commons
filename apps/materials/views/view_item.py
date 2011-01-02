from django.core.urlresolvers import reverse, resolve
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.material import PUBLISHED_STATE, WORKFLOW_TRANSITIONS
from materials.models.microsite import Microsite
from materials.utils import get_name_from_slug
from materials.views.filters import FILTERS
from materials.views.index import PATH_FILTERS, IndexParams, \
    serialize_query_string_params
from notes.models import Note
from tags.models import Tag
from tags.tags_utils import get_tag_cloud


def view_item(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    if hasattr(item, "breadcrumbs"):
        breadcrumbs = item.breadcrumbs
    else:
        breadcrumbs = []

    if request.user.is_authenticated():
        if item.creator == request.user or request.user.is_staff:
            content_actions = [
                {"url": reverse("materials:%s:edit" % item.namespace, kwargs=dict(slug=item.slug)), "title": u"Edit", "class": "edit"},
                {"url": reverse("materials:%s:delete" % item.namespace, kwargs=dict(slug=item.slug)), "title": u"Delete", "class": "delete"},
            ]
        else:
            content_actions = []

        workflow_actions = []
        for transition in WORKFLOW_TRANSITIONS:
            if item.workflow_state in transition["from"] and transition["condition"](request.user, item):
                workflow_actions.append({
                    "url": reverse("materials:%s:transition" % item.namespace, kwargs=dict(slug=item.slug, transition_id=transition["id"])),
                    "title": transition["title"],
                })

    tags = {}
    for tag in item.tags.all():
        tags[tag.slug] = tags.get(tag.slug, 0) + 1
    tags = get_tag_cloud(tags, 3, 0, 1)
    for tag in tags:
        tag["name"] = get_name_from_slug(Tag, tag["slug"])

    user_tags = []
    user_note = None
    save_url = None
    unsave_url = None
    if request.user.is_authenticated():
        user_tags = item.tags.filter(user=request.user).order_by("slug")
        try:
            user_note = item.notes.get(user=request.user)
        except Note.DoesNotExist:
            pass
        try:
            item.saved_items.get(user=request.user)
            unsave_url = reverse("materials:%s:unsave_item" % item.namespace,
                           kwargs=dict(slug=item.slug))

        except:
            save_url = reverse("materials:%s:save_item" % item.namespace,
                           kwargs=dict(slug=item.slug))
    else:
        save_url = reverse("materials:%s:save_item" % item.namespace,
                       kwargs=dict(slug=item.slug))

    add_tags_url = reverse("materials:%s:add_tags" % item.namespace,
                           kwargs=dict(slug=item.slug))
    add_review_url = reverse("materials:%s:add_review" % item.namespace,
                           kwargs=dict(slug=item.slug))
    add_note_url = reverse("materials:%s:add_note" % item.namespace,
                           kwargs=dict(slug=item.slug))
    rate_item_url = reverse("materials:%s:rate_item" % item.namespace,
                           kwargs=dict(slug=item.slug))


    microsite = None
    came_from_index = False

    prev_item_url = u""
    next_item_url = u""
    index_url = u""
    hidden_filters = {}

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
        microsite = kwargs.get("microsite")
        if microsite:
            microsite = Microsite.objects.get(slug=microsite)

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

        index_params = IndexParams(request, search_query=search_query)
        query_string_params = index_params.update_query_string_params(query_string_params)

        if index_params.query_order_by is not None:
            query = query.order_by(index_params.query_order_by)

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

        batch_start = (current_item_idx / index_params.batch_size) * index_params.batch_size
        if batch_start:
            query_string_params["batch_start"] = batch_start

        index_url = index_path + serialize_query_string_params(query_string_params)

    return direct_to_template(request, "materials/view-item.html", locals())
