from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, resolve
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.material import WORKFLOW_TRANSITIONS
from materials.models.microsite import Microsite
from materials.views.filters import FILTERS
from materials.views.index import PATH_FILTERS, IndexParams, \
    serialize_query_string_params
from saveditems.models import SavedItem
from visitcounts.models import Visit
from reviews.views import ReviewForm


def view_item(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    if hasattr(item, "breadcrumbs"):
        breadcrumbs = item.breadcrumbs
    else:
        breadcrumbs = []

    content_type = ContentType.objects.get_for_model(item)

    if request.user.is_authenticated():
        content_actions = []
        if item.creator == request.user or request.user.is_staff:
            content_actions += [
                {"url": reverse("materials:%s:edit" % item.namespace,
                                kwargs=dict(slug=item.slug)),
                 "title": u"Edit",
                 "class": "edit"},
                                
                {"url": reverse("materials:%s:delete" % item.namespace,
                                kwargs=dict(slug=item.slug)),
                 "title": u"Delete",
                 "class": "delete"},
            ]
        if request.user.is_staff:
            content_actions.append({"url": reverse("admin:%s_%s_change" % (content_type.app_label,
                                                                           content_type.model),
                                                   args=(item.id,)),
                                      "title": u"Edit in admin",
                                      "class": "edit"})

        workflow_actions = []
        for transition in WORKFLOW_TRANSITIONS:
            if item.workflow_state in transition["from"] and transition["condition"](request.user, item):
                workflow_actions.append({
                    "url": reverse("materials:%s:transition" % item.namespace,
                                   kwargs=dict(slug=item.slug,
                                               transition_id=transition["id"])),
                    "title": transition["title"],
                })

    user_tags = []
    save_url = None
    unsave_url = None
    if request.user.is_authenticated():
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

    add_review_url = reverse("materials:%s:add_review" % item.namespace,
                           kwargs=dict(slug=item.slug))

    item.identifier = "%s.%s.%i" % (content_type.app_label,
                                    content_type.model,
                                    item.id)
    
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

        query = SearchQuerySet().narrow("is_displayed:true")

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
                        prev_item_url = reverse("materials:%s:view_item" % namespace,
                                                kwargs=dict(slug=prev_item.get_stored_fields()["slug"]))
                    else:
                        prev_item_url = result.object.get_absolute_url()

                if current_item_idx < (len(query) - 1):
                    next_item = query[current_item_idx + 1]
                    namespace = getattr(next_item.model, "namespace", None)
                    if namespace:
                        next_item_url = reverse("materials:%s:view_item" % namespace,
                                                kwargs=dict(slug=next_item.get_stored_fields()["slug"]))
                    else:
                        next_item_url = result.object.get_absolute_url()
                break
            current_item_idx += 1

        batch_start = (current_item_idx / index_params.batch_size) * index_params.batch_size
        if batch_start:
            query_string_params["batch_start"] = batch_start

        index_url = index_path + serialize_query_string_params(query_string_params)

    toolbar_view_url = reverse("materials:%s:toolbar_view_item" % item.namespace,
                                   kwargs=dict(slug=item.slug))

    Visit.objects.count(request, item)

    return direct_to_template(request, "materials/view-item.html", locals())


def toolbar_view_item(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)
    if not item.url:
        raise Http404()

    content_type = ContentType.objects.get_for_model(item)
    item.identifier = "%s.%s.%i" % (content_type.app_label,
                                    content_type.model,
                                    item.id)

    add_tags_url = reverse("tags:add_tags", args=(
                                content_type.app_label,
                                content_type.model,
                                item.id,
                            ))
    
    saved = False
    if request.user.is_authenticated():
        saved = SavedItem.objects.filter(content_type=content_type,
                                         object_id=item.id,
                                         user=request.user).exists()

    save_url = reverse("materials:%s:save_item" % item.namespace,
                   kwargs=dict(slug=item.slug))
    unsave_url = reverse("materials:%s:unsave_item" % item.namespace,
                   kwargs=dict(slug=item.slug))

    add_review_url = reverse("materials:%s:add_review" % item.namespace,
                           kwargs=dict(slug=item.slug))

    if request.user.is_authenticated():
        review_form = ReviewForm(instance=item, user=request.user)
    else:
        review_form = ReviewForm()

    Visit.objects.count(request, item)

    return direct_to_template(request, "materials/toolbar-view-item.html", locals())
