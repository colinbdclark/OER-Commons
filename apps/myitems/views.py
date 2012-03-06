from django import forms
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.http import Http404
from django.contrib.contenttypes.models import ContentType

from haystack.query import SearchQuerySet, SQ
from materials.views.index import IndexParams, populate_item_from_search_result, \
    Pagination
from savedsearches.models import SavedSearch
from utils.decorators import login_required
from annoying.decorators import ajax_request
from core.search import reindex

from myitems.models import Folder, FolderItem


def myitems_index(request, view_name, page_title, no_items_message,
                  filter, only_published=True,
                  template="myitems/saved.html", reverse_params=None):

    index_params = IndexParams(request)
    query_string_params = index_params.update_query_string_params({})

    batch_end = index_params.batch_start + index_params.batch_size

    query = SearchQuerySet()
    if only_published:
        query = query.narrow("is_displayed:true")
    query = query.filter(filter)

    if index_params.query_order_by is not None:
        query = query.order_by(index_params.query_order_by)
    else:
        query = query

    results = query[index_params.batch_start:batch_end]
    user_id = request.user.id
    def add_relation(items):
        for item in items:
            if item["creator"] == user_id:
                item["relation_to_user"] = 'created'
            elif user_id in item["saved_by"]:
                item["relation_to_user"] = 'saved'
        return items
    items = add_relation([populate_item_from_search_result(result) for result in results])

    pagination = Pagination(request.path, query_string_params,
                            index_params.batch_start,
                            index_params.batch_size,
                            len(query))

    return direct_to_template(request, template, {
        'pagination': pagination,
        'items': items,
        'index_params': index_params,
    })


@login_required
def saved(request):
    return myitems_index(request, "myitems", u"My Saved Items",
        u"You have not saved any item yet.", "saved_by", request.user.id,
        template="myitems/saved.html")


@login_required
def rated(request):
    return myitems_index(request, "rated", u"My Rated Items",
        u"You have not rated any item yet.", "rated_by", request.user.id)


@login_required
def tagged(request):
    return myitems_index(request, "tagged", u"My Tagged Items",
        u"You have not tagged any item yet.", "tagged_by", request.user.id)


@login_required
def commented(request):
    return myitems_index(request, "commented", u"My Commented Items",
        u"You have not commented any item yet.", "reviewed_by", request.user.id)


@login_required
def submitted(request):
    return myitems_index(request, "submitted", u"My Submitted Items",
        u"You have not submitted any item yet.", SQ(creator=request.user.id),
         only_published=False)


@login_required
def myitems(request):
    return myitems_index(request, "myitems", u"My Items",
        u"You have not submitted any item yet.",
        SQ(saved_by=request.user.id) | SQ(creator=request.user.id),
        only_published=False)


@login_required
def searches(request):
    page_title = u"My Saved Searches"

    items = list(SavedSearch.objects.filter(user=request.user))
    for item in items:
        item.unsave_item_url = reverse("savedsearches:unsave", kwargs=dict(id=item.id))

    return direct_to_template(request, "myitems/searches.html", locals())



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
    name_to_model = dict(
        (model, ContentType.objects.get(app_label=app_label_ext, model=model).model_class())
        for model in models
    )
    def f(app_label, model_name, object_id):
        if app_label != app_label_ext:
            raise Http404()
        try:
            model = name_to_model[model_name]
        except KeyError:
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
            return { "status": "error"}

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



@login_required
def folder(request, slug=None):
    folder = get_object_or_404(Folder, user=request.user, slug=slug)
    return myitems_index(request, "folder", folder.name,
        u"You have not saved any item yet.", SQ(saved_in_folders=folder.id),
        template="myitems/saved.html", reverse_params={ "slug": slug })
