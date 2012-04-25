from collections import defaultdict
from operator import or_, attrgetter
from itertools import groupby
import datetime
import urllib

from django import forms
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView
from django.views.generic.simple import direct_to_template
from django.utils.decorators import method_decorator
from django.utils.formats import localize
from django.utils.datastructures import SortedDict
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from haystack.query import SQ, SearchQuerySet

from materials.views.index import IndexParams, Pagination
from materials.models import CommunityItem, Course, Library, PUBLISHED_STATE, Material
from materials.views import filters
from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from savedsearches.models import SavedSearch
from utils.decorators import login_required
from annoying.decorators import ajax_request
from core.search import reindex
from saveditems.models import SavedItem
from rubrics.models import Evaluation

from myitems.models import Folder, FolderItem


MINDATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)


SUBMITTED_MODELS = set([
    CommunityItem,
    Course,
    Library,
])

CREATED_MODELS = set([
    AuthoredMaterial,
])



class IndexParamsWithSaveDateSort(IndexParams):
    def __init__(self, *args, **kwargs):
        self.SORT_BY_OPTIONS = kwargs['SORT_BY_OPTIONS']
        del kwargs['SORT_BY_OPTIONS']
        IndexParams.__init__(self, *args, **kwargs)


@login_required
def searches(request):
    items = list(SavedSearch.objects.filter(user=request.user))
    for item in items:
        item.unsave_item_url = reverse("savedsearches:unsave", kwargs=dict(id=item.id))


    return direct_to_template(request, "myitems/searches.html",
        {
            'items': items,
            'saved_search': True,
            'hide_global_notifications': True,
        }
    )



class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ("name", )
        widgets = { "name": forms.TextInput(), }



class FolderCreate(View):
    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        _, created = Folder.objects.get_or_create(
            user=request.user,
            name=request.POST["folder_name"]
        )
        return { "status": "success" if created else "error" }



class FolderDelete(View):
    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        try:
            folder = Folder.objects.get(
                user=request.user,
                id=request.REQUEST["id"]
            )
        except Folder.DoesNotExist:
            pass
        else:
            items = set(x.content_object for x in folder.folderitem_set.all())
            folder.delete()
            for item in items:
                reindex(item)

        return { "status": "success" }



def get_content_object_factory(models):
    content_type_to_model = dict(
        zip(
            [ContentType.objects.get_for_model(model).id for model in models],
            models
        )
    )
    def f(content_type, object_id):
        try:
            model = content_type_to_model[int(content_type)]
        except KeyError, ValueError:
            raise Http404()
        try:
            object_id = int(object_id)
        except ValueError:
            raise Http404()

        return get_object_or_404(model, id=object_id)

    return f


get_material_object_or_404 = get_content_object_factory([
    Course,
    CommunityItem,
    Library,
    AuthoredMaterial,
    AuthoredMaterialDraft,
])


class FolderAddItem(View):
    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        try:
            folder_name = request.REQUEST["folder_name"]
            item_id = request.REQUEST["item_id"]
        except KeyError:
            return { "status": "error"}

        content_type, object_id = item_id.split('.')
        material = get_material_object_or_404(content_type, object_id)
        folder, created = Folder.objects.get_or_create(
            user=request.user,
            name=folder_name
        )
        if isinstance(material, Material):
            creator = material.creator
        elif isinstance(material, AuthoredMaterial):
            creator = material.author
        elif isinstance(material, AuthoredMaterialDraft):
            creator = material.material.author
        else:
            assert False, type(material)

        content_type = ContentType.objects.get_for_id(content_type)

        if creator != request.user:
            SavedItem.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            )

        _, created_fi = FolderItem.objects.get_or_create(
            folder=folder,
            content_type=content_type,
            object_id=object_id
        )
        reindex(material)
        if not created_fi:
            return { "status": "error" }
        to_return = { "status": "success" }
        if created:
            to_return["id"] = folder.id
            to_return["slug"] = folder.slug
        return to_return



class FolderItemDelete(View):
    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        try:
            folder_id = request.REQUEST["folder_id"]
            item_id = request.REQUEST["item_id"]
        except KeyError:
            return { "status": "error" }

        folder = Folder.objects.get(
            user=request.user,
            id=folder_id
        )
        material = get_material_object_or_404(*item_id.split('.'))
        material.folders.filter(folder=folder).delete()
        reindex(material)
        to_return = { "status": "success" }
        return to_return



class ItemDelete(View):
    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        try:
            item_id = request.REQUEST["item_id"]
        except KeyError:
            return { "status": "error"}

        material = get_material_object_or_404(*item_id.split('.'))
        if isinstance(material, Material):
            creator = material.creator
        elif isinstance(material, AuthoredMaterial):
            creator = material.author
        elif isinstance(material, AuthoredMaterialDraft):
            creator = material.material.author
        else:
            assert False, type(material)

        if creator == request.user:
            material.delete()
        else:
            material.saved_items.filter(user=request.user).delete()
            reindex(material)
        to_return = { "status": "success" }
        return to_return



class UserItem(object):
    dummy_thumb = 'myitems-dummy-thumb.png'

    def __init__(self, result, view):
        self.item = result.object
        self.content_type = ContentType.objects.get_for_model(result.model)
        self.identifier = '%s.%s' % (self.content_type.id, self.item.id)


    def __getattr__(self, name):
        return getattr(self.item, name)



class DisplayedItem(UserItem):
    def __init__(self, result, view):
        super(DisplayedItem, self).__init__(result, view)
        self.rating = result.rating
        self.folders = view.folders[self.content_type][self.item.id]



class SubmittedUserItem(DisplayedItem):
    def __init__(self, result, view):
        super(SubmittedUserItem, self).__init__(result, view)
        self.item_class = "submitted" if result.creator == view.user.id else "saved"
        self.relation_to_user = (
            "evaluated"
            if int(result.pk) in view.evaluated_items[self.content_type.id]
            else self.item_class
        )



class CreatedUserItem(DisplayedItem):
    item_class = 'created'
    relation_to_user = 'published'



class DraftUserItem(UserItem):
    dummy_thumb = 'myitems-dummy-thumb-draft.png'

    rating = None
    folders = None

    def __init__(self, item, view):
        super(DraftUserItem, self).__init__(item, view)
        if self.item.material.workflow_state == PUBLISHED_STATE:
            self.relation_to_user = "Unpublished\nChanges"
            self.item_class = "unpublished-changes"
        else:
            self.relation_to_user = "Draft"
            self.item_class = "draft"
        self.title = " - ".join((
            self.item.title or self.item.material.title or "Untitled",
            localize(self.item.modified_timestamp or self.item.created_timestamp)
        ))


    def get_absolute_url(self):
        return reverse("authoring:edit", kwargs=dict(pk=self.material.pk))



class MaterialsIndex(object):
    MODEL_TO_WRAPPER = {
        CommunityItem: SubmittedUserItem,
        Course: SubmittedUserItem,
        Library: SubmittedUserItem,
        AuthoredMaterial: CreatedUserItem,
        AuthoredMaterialDraft: DraftUserItem,
    }


    def __init__(self, results, user, model_to_pks,
                    get_folders=True, get_evaluations=True):
        self.results = results
        self.user = user
        self.model_to_pks = model_to_pks

        if get_folders:
            self.get_folders()

        if get_evaluations:
            self.get_evaluations()

        self.items = [
            self.MODEL_TO_WRAPPER[result.model](result, self)
            for result in self.results
        ]


    def get_evaluations(self):
        self.evaluated_items = defaultdict(set)
        query = reduce(or_, (
            Q(
                content_type=ContentType.objects.get_for_model(model),
                object_id__in=self.model_to_pks[model]
            )
            for model in SUBMITTED_MODELS
        ))
        queryset_eval = Evaluation.objects.filter(user=self.user, confirmed=True).filter(query)
        for content_type, object_id in queryset_eval.values_list('content_type', 'object_id'):
            self.evaluated_items[content_type].add(object_id)


    def get_folders(self):
        self.folders = defaultdict(lambda: defaultdict(list))
        query = reduce(or_, (
            Q(
                content_type=ContentType.objects.get_for_model(model),
                object_id__in=self.model_to_pks[model]
            )
            for model in SUBMITTED_MODELS | CREATED_MODELS
        ))
        folder_items = FolderItem.objects.filter(folder__user=self.user
            ).filter(query).select_related("folder", "content_type")
        for fi in folder_items:
            self.folders[fi.content_type][fi.object_id].append(fi.folder)



class MyItemsView(TemplateView):
    template_name = 'myitems/myitems.html'

    slug = "myitems"
    name = "All"
    no_items_message = "You have not any item yet."

    SORT_BY_OPTIONS = (
        {"value": u"title", "title": u"Title"},
        {"value": u"rating", "title": u"Rating"},
        {"value": u"visits", "title": u"Visits"},
        {"value": u"date", "title": u"Date"},
        {"value": u"save_date", "title": u"Save Date"},
    )

    search_filter = filters.FILTERS["search"]

    get_folders = True
    get_evaluations = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyItemsView, self).dispatch(request, *args, **kwargs)


    def render_to_response(self, context, **response_kwargs):
        response = super(MyItemsView, self).render_to_response(
                context, **response_kwargs)
        response.set_cookie("index_type", self.index_type)
        return response


    @classmethod
    def get_count(cls, user):
        return cls.get_queryset(user).count()


    def get_results(self):
        batch_end = self.index_params.batch_start + self.index_params.batch_size
        queryset = self.queryset

        if self.index_params.sort_by == "save_date":
            to_sort = defaultdict(dict)
            to_not_sort = []
            queryset = queryset.order_by("django_ct")
            for model, g in groupby(queryset, attrgetter("model")):
                if model in SUBMITTED_MODELS:
                    ct = ContentType.objects.get_for_model(model).id
                    for result in g:
                        if result.creator == self.user:
                            to_not_sort.append(result)
                        else:
                            to_sort[ct][int(result.pk)] = result
                else:
                    to_not_sort.extend(g)

            results = []

            to_sort_total_items = reduce(lambda x, y: x+len(y), to_sort.itervalues(), 0)
            if self.index_params.batch_start < to_sort_total_items:
                query = reduce(or_, (
                    Q(
                        content_type=ct,
                        object_id__in=results.keys()
                    )
                    for ct, results in to_sort.iteritems()
                ))
                saved_items = SavedItem.objects.filter(user=self.user).filter(query).order_by("-timestamp")
                end = min(self.index_params.batch_start+to_sort_total_items, batch_end)
                results.extend(
                    to_sort[ct][oid]
                    for ct, oid in saved_items.values_list(
                        "content_type", "object_id")[self.index_params.batch_start:end]
                )
            to_add = min(self.index_params.batch_size - len(results), len(to_not_sort))
            results.extend(to_not_sort[:to_add])
            model_to_pks = defaultdict(list)
            for result in results:
                model_to_pks[result.model].append(result.pk)

            items_dict = dict(
                (model,
                    dict(
                        (x.id, x)
                        for x in model.objects.filter(id__in=pks)
                    )
                )
                for model, pks in model_to_pks.iteritems()
            )

            for result in results:
                result.object = items_dict[result.model][int(result.pk)]
        else:
            if self.index_params.query_order_by is not None:
                queryset = queryset.order_by(self.index_params.query_order_by)
            queryset = queryset.load_all()
            results = queryset[self.index_params.batch_start:batch_end]
            model_to_pks = defaultdict(list)
            for x in results:
                model_to_pks[x.model].append(x.pk)

        self.results = results
        self.model_to_pks = model_to_pks


    def narrow_by_search(self):
        if self.search_value:
            self.query_string_params = self.search_filter.update_query_string_params(self.query_string_params, self.search_value)
            self.queryset = self.search_filter.update_query(self.queryset, self.search_value)
            self.SORT_BY_OPTIONS = self.__class__.SORT_BY_OPTIONS+({"value": u"search", "title": u"Relevance"},)


    def get_search_url(self):
        return self.request.path


    def get_context_data(self, *args, **kwargs):
        index_types = SortedDict([
            ("pics", {
                "human_name": "Thumbnails",
                "icon": "myitems-view-thumbnail.png",
                "icon_selected": "myitems-view-thumbnail-selected.png"
            }),
            ("compact", {
                "human_name": "Compact",
                "icon": "myitems-view-compact.png",
                "icon_selected": "myitems-view-compact-selected.png"
            }),
        ])

        user = self.request.user
        self.user = user
        self.query_string_params = {}
        self.queryset = self.get_queryset(user)
        self.search_value = self.search_filter.extract_value(self.request)
        self.narrow_by_search()


        index_type = self.request.GET.get("index_type") or self.request.COOKIES.get("index_type")
        if index_type not in index_types:
            index_type = "pics"
        index_types[index_type]["selected"] = True

        self.index_params = IndexParamsWithSaveDateSort(
            self.request,
            SORT_BY_OPTIONS=self.SORT_BY_OPTIONS,
            search_query=self.search_value
        )
        self.query_string_params = self.index_params.update_query_string_params(self.query_string_params)

        current_query_string_params = self.request.GET.copy()
        for index_type_name, index_type_dict in index_types.iteritems():
            current_query_string_params["index_type"] = index_type_name
            index_type_dict['url'] = '?'.join(
                (self.request.path, urllib.urlencode(current_query_string_params)))
            index_type_dict['name'] = index_type_name

        self.index_type = index_type

        self.get_results()
        materials_index = MaterialsIndex(
            self.results,
            user,
            self.model_to_pks,
            self.get_folders,
            self.get_evaluations,
        )

        total_items = self.queryset.count()
        pagination = Pagination(self.request.path, self.query_string_params,
                        self.index_params.batch_start,
                        self.index_params.batch_size,
                        total_items)

        return {
            'pagination': pagination,
            'items': materials_index.items,
            'index_params': self.index_params,
            'hide_global_notifications': True,
            'index_types': index_types.values(),
            'index_type': index_type,
            'no_items_message': self.no_items_message,
            'page_title': self.name,
            'search_url': self.get_search_url,
            'search_value': self.search_value,
        }


def django_ct_from_model(model):
    ct = ContentType.objects.get_for_model(model)
    return '.'.join((ct.app_label, ct.model))



class AllItems(MyItemsView):
    @classmethod
    def get_queryset(cls, user):
        queryset = SearchQuerySet()
        queryset = queryset.models(*SUBMITTED_MODELS | CREATED_MODELS)

        submitted_query = (
            reduce(or_, (SQ(django_ct=django_ct_from_model(model)) for model in SUBMITTED_MODELS))
            & (SQ(creator=user.id) | SQ(saved_by=user.id))
        )
        created_query = (
            reduce(or_, (SQ(django_ct=django_ct_from_model(model)) for model in CREATED_MODELS))
            & SQ(creator=user.id, is_displayed=True)
        )
        queryset = queryset.filter(submitted_query | created_query)

        return queryset



class SubmittedItems(MyItemsView):
    slug = "submitted"
    name = "Submitted Items"
    no_items_message = "You have not submitted any item yet."

    @classmethod
    def get_queryset(cls, user):
        queryset = SearchQuerySet()
        queryset = queryset.models(*SUBMITTED_MODELS)

        submitted_query = (
            reduce(or_, (SQ(django_ct=django_ct_from_model(model)) for model in SUBMITTED_MODELS))
            & SQ(creator=user.id)
        )
        queryset = queryset.filter(submitted_query)

        return queryset



class PublishedItems(MyItemsView):
    slug = "published"
    name = "Published Items"
    no_items_message = "You have not published any item yet."

    @classmethod
    def get_queryset(cls, user):
        queryset = SearchQuerySet()
        queryset = queryset.models(*CREATED_MODELS)
        queryset = queryset.narrow("is_displayed:true")
        queryset = queryset.filter(SQ(creator=user.id))

        return queryset



class ResultLike(object):
    rating = None

    def __init__(self, item, model):
        self.object = item
        self.model = model



class DraftItems(MyItemsView):
    slug = "draft"
    name = "Draft Items"
    no_items_message = "You have no draft items yet."
    show_item_folders = False

    SORT_BY_OPTIONS = (
        {"value": u"title", "title": u"Title"},
        {"value": u"date", "title": u"Date"},
    )

    DRAFT_MODEL = AuthoredMaterialDraft

    model_to_pks = None
    get_folders = False
    get_evaluations = False
    get_search_url = None

    @classmethod
    def get_queryset(cls, user):
        return cls.DRAFT_MODEL.objects.filter(material__author=user
                                                ).select_related("material")


    @classmethod
    def sort_by_title(cls, queryset):
        return queryset.order_by("title")


    @classmethod
    def sort_by_date(cls, queryset):
        return queryset.order_by("-modified_timestamp")


    def get_results(self):
        sort_by = self.index_params.sort_by
        queryset = self.queryset
        if sort_by:
            queryset = getattr(self, "sort_by_%s" % sort_by)(queryset)
        batch_end = self.index_params.batch_start+self.index_params.batch_size

        self.results = [
            ResultLike(item, self.DRAFT_MODEL)
            for item in queryset[self.index_params.batch_start:batch_end]
        ]



class FolderItems(MyItemsView):
    no_items_message = u"You have not saved any item in this folder yet."

    def get_queryset(self, user):
        queryset = SearchQuerySet()
        ct_to_pks = defaultdict(list)
        folder_items = FolderItem.objects.filter(folder=self.folder)
        for ct, pk in folder_items.values_list('content_type', 'object_id'):
            ct_to_pks[ContentType.objects.get_for_id(ct)].append(pk)

        if ct_to_pks:
            query = reduce(or_,(
                SQ(django_ct='.'.join((ct.app_label, ct.model)), django_id__in=pks)
                for ct, pks in ct_to_pks.iteritems()
            ))
            return queryset.filter(query)
        else:
            return queryset.none()


    def get_context_data(self, *args, **kwargs):
        self.slug = kwargs['slug']
        self.folder = get_object_or_404(Folder, user=self.request.user, slug=self.slug)
        self.name = self.folder.name
        return super(FolderItems, self).get_context_data(*args, **kwargs)
