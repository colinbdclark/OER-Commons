from collections import defaultdict
from operator import itemgetter, attrgetter
import datetime
import urllib

from django import forms
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView
from django.views.generic.simple import direct_to_template
from django.utils.decorators import method_decorator
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.db.models import Q

from materials.views.index import IndexParams, Pagination
from materials.models import CommunityItem, Course, Library, PUBLISHED_STATE
from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from savedsearches.models import SavedSearch
from utils.decorators import login_required
from annoying.decorators import ajax_request
from core.search import reindex
from saveditems.models import SavedItem
from rubrics.models import Evaluation

from myitems.models import Folder, FolderItem


MINDATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)


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


class FolderItemForm(forms.ModelForm):
    class Meta:
        model = FolderItem
        fields = ("folder", )
        widgets = { "folder": forms.TextInput(), }



class FolderCreate(View):
    form_class = FolderForm

    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        form = self.form_class(
            instance=Folder(user=request.user),
            data=request.POST
        )
        if form.is_valid():
            folder = form.save()
            return {
                "status": "success",
                "slug": folder.slug,
                "name": folder.name,
                "id": folder.id
            }
        else:
            return { "status": "error" }



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



def get_content_object_factory(app_label_ext, models):
    content_types = (
        ContentType.objects.get(app_label=app_label_ext, model=model)
        for model in models
    )

    name_to_model = dict(
        (content_type.id, content_type.model_class())
        for content_type in content_types
    )
    def f(content_type, object_id):
        try:
            model = name_to_model[int(content_type)]
        except KeyError, ValueError:
            raise Http404()
        try:
            object_id = int(object_id)
        except ValueError:
            raise Http404()

        return get_object_or_404(model, id=object_id)

    return f



get_material_object_or_404 = get_content_object_factory(
    "materials", ["course", "library", "communityitem"])



class FolderAddItem(View):
    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        try:
            folder_name = request.REQUEST["folder_name"]
            item_id = request.REQUEST["item_id"]
        except KeyError:
            return { "status": "error"}

        folder, created = Folder.objects.get_or_create(
            user=request.user,
            name=folder_name
        )
        material = get_material_object_or_404(*item_id.split('.'))
        FolderItem.objects.create(folder=folder, content_object=material)
        reindex(material)
        to_return = { "status": "success" }
        if created:
            to_return["folder_id"] = folder.id
            to_return["folder_slug"] = folder.slug
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
        if material.creator == request.user:
            material.delete()
        else:
            material.saved_items.filter(user=request.user).delete()
            material.folders.filter(folder__user=request.user).delete()
            reindex(material)
        to_return = { "status": "success" }
        return to_return



class UserItem(object):
    def __init__(self, item, content_type, user):
        self.item = item
        self.content_type = content_type
        self.user = user
        self.identifier = '%s.%s' % (content_type.id, item.id)


    def folders(self):
        return (x.folder for x in FolderItem.objects.filter(
                content_type=self.content_type,
                object_id=self.item.id,
                folder__user=self.user,
            )
        )


    def __getattr__(self, name):
        return getattr(self.item, name)



class SubmittedUserItem(UserItem):
    def relation_to_user(self):
        if Evaluation.objects.filter(user=self.user,
                                     content_type=self.content_type,
                                     object_id=self.item.id,
                                     confirmed=True).exists():
            return 'evaluated'
        elif self.item.creator == self.user:
            return 'submitted'
        else:
            return 'saved'


    @property
    def date(self):
        return self.published_on or datetime.datetime(datetime.MINYEAR, 1, 1)



class CreatedUserItem(UserItem):
    def relation_to_user(self):
        return 'created'


    @property
    def date(self):
        return self.created_timestamp



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

    SUBMITTED_MODELS = set([
        CommunityItem,
        Course,
        Library,
    ])

    CREATED_MODELS = set([
        AuthoredMaterial,
    ])


    @staticmethod
    def sort_by_title(items):
        items.sort(key=attrgetter('title'))


    @staticmethod
    def sort_by_rating(items):
        items.sort(key=lambda x: getattr(x, 'rating', 0), reverse=True)


    @staticmethod
    def sort_by_visits(items):
        items.sort(key=attrgetter('visits'), reverse=True)


    @staticmethod
    def sort_by_date(items):
        items.sort(key=attrgetter('date'), reverse=True)


    def sort_by_save_date(self, items):
        type_to_pks = defaultdict(list)
        for item in items:
            type_to_pks[item.content_type].append(item.pk)

        d = {}
        for content_type, pks in type_to_pks.iteritems():
            d[content_type] = dict(SavedItem.objects.filter(
                        user=self.request.user, content_type=content_type,
                        object_id__in=pks).values_list('object_id', 'timestamp'))

        items.sort(key=lambda x: d[x.content_type].get(x.pk, MINDATETIME), reverse=True)


    @classmethod
    def get_count(cls, user):
        return sum(x[0].count() for x in cls.get_querysets(user))


    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyItemsView, self).dispatch(request, *args, **kwargs)


    def render_to_response(self, context, **response_kwargs):
        response = super(MyItemsView, self).render_to_response(
                context, **response_kwargs)
        response.set_cookie("index_type", self.index_type)
        return response



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

        index_type = self.request.GET.get("index_type") or self.request.COOKIES.get("index_type")
        if index_type not in index_types:
            index_type = "pics"
        index_types[index_type]["selected"] = True

        index_params = IndexParamsWithSaveDateSort(
                self.request, SORT_BY_OPTIONS=self.SORT_BY_OPTIONS)
        query_string_params = index_params.update_query_string_params({})

        batch_end = index_params.batch_start + index_params.batch_size


        current_query_string_params = self.request.GET.copy()
        for index_type_name, index_type_dict in index_types.iteritems():
            current_query_string_params["index_type"] = index_type_name
            index_type_dict['url'] = '?'.join(
                (self.request.path, urllib.urlencode(current_query_string_params)))
            index_type_dict['name'] = index_type_name

        self.index_type = index_type


        items = []
        user = self.request.user

        querysets = self.get_querysets(user)

        items = [
            wrapper(item, content_type, user)
            for queryset, content_type, wrapper in self.get_querysets(user)
            for item in queryset
        ]
        getattr(self, 'sort_by_%s' % index_params.sort_by)(items)
        items = items[index_params.batch_start:batch_end]

        pagination = Pagination(self.request.path, query_string_params,
                        index_params.batch_start,
                        index_params.batch_size,
                        sum(x[0].count() for x in querysets))

        return {
            'pagination': pagination,
            'items': items,
            'index_params': index_params,
            'hide_global_notifications': True,
            'index_types': index_types.values(),
            'index_type': index_type,
            'no_items_message': self.no_items_message,
            'page_title': self.name,
        }



class AllItems(MyItemsView):
    @classmethod
    def get_querysets(cls, user):
        querysets = []

        for model in cls.SUBMITTED_MODELS:
            content_type = ContentType.objects.get_for_model(model)
            saved_items = SavedItem.objects.filter(
                content_type=content_type, user=user)
            saved_items_ids = saved_items.values_list('object_id', flat=True)
            filter_query = Q(creator=user) | Q(id__in=saved_items_ids)
            querysets.append((model.objects.filter(filter_query), content_type, SubmittedUserItem))

        for model in cls.CREATED_MODELS:
            content_type = ContentType.objects.get_for_model(model)
            querysets.append((
                model.objects.filter(author=user, workflow_state=PUBLISHED_STATE),
                content_type, CreatedUserItem
            ))

        return querysets



class SubmittedItems(MyItemsView):
    slug = "submitted"
    name = "My Submitted Items"
    no_items_message = "You have not submitted any item yet."

    @classmethod
    def get_querysets(cls, user):
        querysets = []

        for model in cls.SUBMITTED_MODELS:
            content_type = ContentType.objects.get_for_model(model)
            querysets.append((model.objects.filter(Q(creator=user)), content_type, SubmittedUserItem))

        return querysets



class PublishedItems(MyItemsView):
    slug = "published"
    name = "My Published Items"
    no_items_message = "You have not published any item yet."

    @classmethod
    def get_querysets(cls, user):
        querysets = []

        for model in cls.CREATED_MODELS:
            content_type = ContentType.objects.get_for_model(model)
            querysets.append((
                model.objects.filter(author=user, workflow_state=PUBLISHED_STATE),
                content_type, CreatedUserItem
            ))

        return querysets



class DraftItems(MyItemsView):
    slug = "draft"
    name = "My Draft Items"
    no_items_message = "You have no draft items yet."

    SORT_BY_OPTIONS = (
        {"value": u"title", "title": u"Title"},
    )

    @classmethod
    def get_querysets(cls, user):
        querysets = []

        for model in [AuthoredMaterialDraft]:
            content_type = ContentType.objects.get_for_model(model)
            querysets.append((
                model.objects.filter(material__author=user),
                content_type, CreatedUserItem
            ))

        return querysets



class FolderItems(MyItemsView):
    no_items_message = u"You have not saved any item in this folder yet."


    def get_querysets(self, user):
        querysets = []
        type_to_pks = defaultdict(list)
        folder_items = FolderItem.objects.filter(folder=self.folder)
        folder_items_pks = folder_items.values_list('content_type', 'object_id')
        for content_type, pk in folder_items_pks:
            type_to_pks[content_type].append(pk)

        for content_type_pk, pks in type_to_pks.iteritems():
            content_type = ContentType.objects.get(pk=content_type_pk)
            model = content_type.model_class()
            wrapper = SubmittedUserItem if model in self.SUBMITTED_MODELS else CreatedUserItem
            querysets.append((
                model.objects.filter(pk__in=pks),
                content_type, wrapper
            ))

        return querysets


    def get_context_data(self, *args, **kwargs):
        self.slug = kwargs['slug']
        self.folder = get_object_or_404(Folder, user=self.request.user, slug=self.slug)
        self.name = self.folder.name
        return super(FolderItems, self).get_context_data(*args, **kwargs)


