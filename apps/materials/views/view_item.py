from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, resolve
from django.db.models import Avg, Count
from django.http import Http404, QueryDict, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDict
from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.material import WORKFLOW_TRANSITIONS, PUBLISHED_STATE
from materials.models.microsite import Microsite
from materials.views.filters import FILTERS
from materials.views.index import PATH_FILTERS, IndexParams, \
    serialize_query_string_params
from reviews.views import ReviewForm
from rubrics.models import StandardAlignmentScore, RubricScore, Rubric
from saveditems.models import SavedItem
from visitcounts.models import Visit
import urllib





# TODO: rewrite this to class based view when project is moved to Django 1.3
# This would allow to avoid code duplication.


class DummyRequest(HttpRequest):

    def __init__(self, data=None):
        if not data:
            data = {}
        self.REQUEST = MultiValueDict(data)
        super(DummyRequest, self).__init__()


def view_item(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    # Not published item is shown only to staff users or to the user that added it.
    if item.workflow_state != PUBLISHED_STATE:
        if request.user.is_anonymous():
            raise Http404()
        elif not request.user.is_staff and not request.user.is_superuser and request.user != item.creator:
            raise Http404()

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

    tags = []
    tags_slugs = set()
    microsite_markers = set()
    for microsite in Microsite.objects.all():
        microsite_markers.update(microsite.keywords.values_list("slug", flat=True))


    user_tags = []
    if request.user.is_authenticated():
        user_tags = item.tags.filter(user=request.user).values("id", "slug", "name")
        for tag in user_tags:
            tag["class"] = "tag"
            tags_slugs.add(tag["slug"])

    for topic in item.topics():
        tag = {"class": "topic", "slug": topic.slug, "name": topic.name,
               "microsite": topic.microsite, "other": topic.other}
        tags_slugs.add(tag["slug"])
        tags.append(tag)

    for tag in item.keywords.exclude(slug__in=tags_slugs | microsite_markers).values("id", "slug", "name"):
        tag["class"] = "keyword"
        tags_slugs.add(tag["slug"])
        tags.append(tag)

    for tag in item.tags.exclude(slug__in=tags_slugs | microsite_markers).values("id", "slug", "name"):
        if tag["slug"] in tags_slugs:
            continue
        tag["class"] = "tag"
        tags_slugs.add(tag["slug"])
        tags.append(tag)

    tags.sort(key=lambda tag: tag["slug"])



    microsite = None
    came_from_index = False

    prev_item_url = u""
    next_item_url = u""
    index_url = u""
    hidden_filters = {}

    kwargs = {}

    filters = {}
    index_path = None

    if "_i" in request.COOKIES:
        filters = dict(QueryDict(urllib.unquote(request.COOKIES["_i"])))
        index_path = filters.pop("index_path", None)
        if index_path and isinstance(index_path, list):
            index_path = index_path[0]
            
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

        dummy_request = DummyRequest(filters)
        for filter_name, filter in FILTERS.items():
            if filter_name == path_filter:
                continue
            value = filter.extract_value(dummy_request)
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
        item_found = False
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
                item_found = True
                break
            current_item_idx += 1

        batch_start = (current_item_idx / index_params.batch_size) * index_params.batch_size
        if batch_start:
            query_string_params["batch_start"] = batch_start

        if item_found:
            index_url = index_path + serialize_query_string_params(query_string_params)

    toolbar_view_url = reverse("materials:%s:toolbar_view_item" % item.namespace,
                                   kwargs=dict(slug=item.slug))

    # Evaluation scores
    evaluations_number = 0
    evaluation_scores = []

    alignment_scores = StandardAlignmentScore.objects.filter(
        content_type=content_type,
        object_id=item.id,
    )

    evaluations_number = len(alignment_scores.values_list("user__id", flat=True).distinct())

    average_score = alignment_scores.aggregate(
        Avg("score__value")
    )["score__value__avg"]
    if average_score is None:
        average_score_class = None
    else:
        average_score_class = int(average_score)

    evaluation_scores.append(dict(
        name=u"Degree of Alignment",
        average_score=average_score,
        average_score_class=average_score_class,
    ))

    rubric_scores = RubricScore.objects.filter(
        content_type=content_type,
        object_id=item.id,
    )
    for rubric in Rubric.objects.all():
        scores = rubric_scores.filter(rubric=rubric)
        evaluations_number = max(
            evaluations_number,
            len(scores.values_list("user__id", flat=True).distinct())
        )

        average_score =scores.aggregate(
            Avg("score__value")
        )["score__value__avg"]

        if average_score is None:
            average_score_class = None
        else:
            average_score_class = int(average_score)

        evaluation_scores.append(dict(
            name=rubric.name,
            average_score=average_score,
            average_score_class=average_score_class,
        ))

    Visit.objects.count(request, item)

    return direct_to_template(request, "materials/view-item.html", locals())


def toolbar_view_item(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)
    if not item.url:
        raise Http404()

    # Not published item is shown only to staff users or to the user that added it.
    if item.workflow_state != PUBLISHED_STATE:
        if request.user.is_anonymous():
            raise Http404()
        elif not request.user.is_staff and not request.user.is_superuser and request.user != item.creator:
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

    microsite = None
    came_from_index = False

    prev_item_url = u""
    next_item_url = u""
    index_url = u""
    hidden_filters = {}

    kwargs = {}
    filters = {}
    index_path = None

    if "_i" in request.COOKIES:
        filters = dict(QueryDict(urllib.unquote(request.COOKIES["_i"])))
        index_path = filters.pop("index_path", None)
        if index_path and isinstance(index_path, list):
            index_path = index_path[0]

    if index_path:
        try:
            kwargs = resolve(index_path)[2]
            came_from_index = True
        except Http404:
            pass

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

        dummy_request = DummyRequest(filters)
        for filter_name, filter in FILTERS.items():
            if filter_name == path_filter:
                continue
            value = filter.extract_value(dummy_request)
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
        item_found = False
        for result in query:
            if result.model == model and int(result.pk) == item.id:
                if current_item_idx > 0:
                    prev_item = query[current_item_idx - 1]
                    namespace = getattr(prev_item.model, "namespace", None)
                    if namespace:
                        prev_item_url = reverse("materials:%s:toolbar_view_item" % namespace, kwargs=dict(slug=prev_item.get_stored_fields()["slug"]))
                    else:
                        prev_item_url = result.object.get_absolute_url()

                if current_item_idx < (len(query) - 1):
                    next_item = query[current_item_idx + 1]
                    namespace = getattr(next_item.model, "namespace", None)
                    if namespace:
                        next_item_url = reverse("materials:%s:toolbar_view_item" % namespace, kwargs=dict(slug=next_item.get_stored_fields()["slug"]))
                    else:
                        next_item_url = result.object.get_absolute_url()
                item_found = True
                break
            current_item_idx += 1

        batch_start = (current_item_idx / index_params.batch_size) * index_params.batch_size
        if batch_start:
            query_string_params["batch_start"] = batch_start

        if item_found:
            index_url = index_path + serialize_query_string_params(query_string_params)

    Visit.objects.count(request, item)

    return direct_to_template(request, "materials/toolbar-view-item.html", locals())
