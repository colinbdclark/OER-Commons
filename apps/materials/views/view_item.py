from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, resolve
from django.http import Http404, QueryDict, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDict
from django.views.generic.base import TemplateView
from haystack.query import SearchQuerySet
from materials.models.material import WORKFLOW_TRANSITIONS, PUBLISHED_STATE
from materials.models.microsite import Microsite
from materials.utils import get_name_from_id
from materials.views.filters import FILTERS
from materials.views.index import PATH_FILTERS, IndexParams, \
    serialize_query_string_params
from reviews.views import ReviewForm
from rubrics.models import Rubric
from saveditems.models import SavedItem
from visitcounts.models import Visit
import urllib


class DummyRequest(HttpRequest):

    def __init__(self, data=None):
        if not data:
            data = {}
        self.REQUEST = MultiValueDict(data)
        super(DummyRequest, self).__init__()


#noinspection PyUnresolvedReferences
class BaseViewItemMixin(object):

    def get(self, request, *args, **kwargs):
        self.slug = kwargs["slug"]
        self.model = kwargs["model"]
        if not self.slug or not self.model:
            raise Http404()
        self.item = get_object_or_404(self.model, slug=self.slug)

        # Not published item is shown only to staff users or to the user that added it.
        if self.item.workflow_state != PUBLISHED_STATE:
            if request.user.is_anonymous():
                raise Http404()
            elif not request.user.is_staff and not request.user.is_superuser and request.user != self.item.creator:
                raise Http404()

        self.content_type = ContentType.objects.get_for_model(self.item)

        self.item.identifier = "%s.%s.%i" % (self.content_type.app_label,
                                            self.content_type.model,
                                            self.item.id)

        Visit.objects.count(request, self.item)

        return super(BaseViewItemMixin, self).get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        data = super(BaseViewItemMixin, self).get_context_data(**kwargs)

        item = self.item
        request = self.request
        model = self.model
        content_type = self.content_type

        data["item"] = self.item

        microsite = None
        came_from_index = False

        prev_item_url = u""
        next_item_url = u""
        index_url = u""
        index_params = None
        hidden_filters = {}

        kwargs = {}

        filters = {}
        index_path = None

        if "_i" in request.COOKIES:
            filters = dict(QueryDict(urllib.unquote(request.COOKIES["_i"])))
            #noinspection PyArgumentEqualDefault
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
                value = kwargs.get(filter_name)
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
                            prev_item_url = reverse("materials:%s:%s" % (namespace, self.view_item_name),
                                                    kwargs=dict(slug=prev_item.get_stored_fields()["slug"]))
                        else:
                            prev_item_url = result.object.get_absolute_url()

                    if current_item_idx < (len(query) - 1):
                        next_item = query[current_item_idx + 1]
                        namespace = getattr(next_item.model, "namespace", None)
                        if namespace:
                            next_item_url = reverse("materials:%s:%s" % (namespace, self.view_item_name),
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

        data["microsite"] = microsite
        data["came_from_index"] = came_from_index
        data["index_path"] = index_path
        data["index_params"] = index_params
        data["index_url"] = index_url
        data["hidden_filters"] = hidden_filters
        data["prev_item_url"] = prev_item_url
        data["next_item_url"] = next_item_url

        if request.user.is_authenticated():
            data["saved"] = SavedItem.objects.filter(
                content_type=content_type,
                object_id=item.id,
                user=request.user
            ).exists()

        data["save_url"] = reverse("materials:%s:save_item" % item.namespace,
                       kwargs=dict(slug=item.slug))
        data["unsave_url"] = reverse("materials:%s:unsave_item" % item.namespace,
                       kwargs=dict(slug=item.slug))

        data["add_review_url"] = reverse("materials:%s:add_review" % item.namespace,
                               kwargs=dict(slug=item.slug))

        data["add_tags_url"] = reverse("tags:add_tags", args=(
            content_type.app_label,
            content_type.model,
            item.id,
        ))

        return data


class ViewItem(BaseViewItemMixin, TemplateView):

    template_name = "materials/view-item.html"
    view_item_name = "view_item"

    def get_context_data(self, **kwargs):
        data = super(ViewItem, self).get_context_data(**kwargs)

        item = self.item
        request = self.request

        data["breadcrumbs"] = getattr(item, "breadcrumbs", [])

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
                content_actions.append({
                    "url": reverse("admin:%s_%s_change" % (self.content_type.app_label,
                                                        self.content_type.model),
                                                        args=(item.id,)),
                    "title": u"Edit in admin",
                    "class": "edit"
                })

            workflow_actions = []
            for transition in WORKFLOW_TRANSITIONS:
                if item.workflow_state in transition["from"] and transition["condition"](request.user, item):
                    workflow_actions.append({
                        "url": reverse("materials:%s:transition" % item.namespace,
                                       kwargs=dict(slug=item.slug,
                                                   transition_id=transition["id"])),
                        "title": transition["title"],
                    })

        tags = []
        tags_slugs = set()
        microsite_markers = set()

        for microsite in Microsite.objects.all():
            microsite_markers.update(microsite.keywords.values_list("slug", flat=True))

        if request.user.is_authenticated():
            user_tags = item.tags.filter(user=request.user).values("id", "slug", "name")
            for tag in user_tags:
                tag["class"] = "tag"
                tags_slugs.add(tag["slug"])
            data["user_tags"] = user_tags

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

        data["tags"] = tags

        data["evaluations_number"] = item.evaluations_number
        data["evaluation_scores"] = []

        for rubric_id, score in sorted(item.evaluation_scores.items()):
            #noinspection PySimplifyBooleanCheck
            if rubric_id == 0:
                name = u"Degree of Alignment"
            else:
                name = get_name_from_id(Rubric, rubric_id)
            if score is None:
                score_class = None
            else:
                score_class = int(score)
            data["evaluation_scores"].append(dict(name=name, score=score, score_class=score_class))

        data["toolbar_view_url"] = reverse("materials:%s:toolbar_view_item" % item.namespace,
                                       kwargs=dict(slug=item.slug))

        return data


class ToolbarViewItem(BaseViewItemMixin, TemplateView):

    template_name = "materials/toolbar-view-item.html"
    view_item_name = "toolbar_view_item"

    def get_context_data(self, **kwargs):
        data = super(ToolbarViewItem, self).get_context_data(**kwargs)

        item = self.item
        request = self.request

        if request.user.is_authenticated():
            data["review_form"] = ReviewForm(instance=item, user=request.user)
        else:
            data["review_form"] = ReviewForm()

        return data
