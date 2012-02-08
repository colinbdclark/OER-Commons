from django import forms
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.views.generic import CreateView
from django.utils.decorators import method_decorator

from haystack.query import SearchQuerySet
from materials.views.index import IndexParams, populate_item_from_search_result, \
    Pagination
from savedsearches.models import SavedSearch
from utils.decorators import login_required
from annoying.decorators import ajax_request

from myitems.models import Folder


def myitems_index(request, view_name, page_title, no_items_message, index_name,
                  only_published=True, template="myitems/index.html"):

    breadcrumbs = [
        {"url": reverse("myitems:myitems"), "title": u"My Items"},
        {"url": reverse("myitems:%s" % view_name), "title": page_title},
    ]

    query_string_params = {}
    index_params = IndexParams(request)
    query_string_params = index_params.update_query_string_params(query_string_params)

    batch_end = index_params.batch_start + index_params.batch_size

    query = SearchQuerySet()
    if only_published:
        query = query.narrow("is_displayed:true")
    query = query.narrow("%s:%i" % (index_name, request.user.id))

    if index_params.query_order_by is not None:
        query = query.order_by(index_params.query_order_by)

    items = []
    results = query[index_params.batch_start:batch_end]
    for result in results:
        items.append(populate_item_from_search_result(result))

    pagination = Pagination(request.path, query_string_params,
                            index_params.batch_start,
                            index_params.batch_size,
                            len(query))


    return direct_to_template(request, template, locals())


@login_required
def saved(request):
    return myitems_index(request, "myitems", u"My Saved Items", u"You have not saved any item yet.", "saved_by",
                         template="myitems/saved.html")


@login_required
def rated(request):
    return myitems_index(request, "rated", u"My Rated Items", u"You have not rated any item yet.", "rated_by")


@login_required
def tagged(request):
    return myitems_index(request, "tagged", u"My Tagged Items", u"You have not tagged any item yet.", "tagged_by")


@login_required
def commented(request):
    return myitems_index(request, "commented", u"My Commented Items", u"You have not commented any item yet.", "reviewed_by")


@login_required
def submitted(request):
    return myitems_index(request, "submitted", u"My Submitted Items", u"You have not submitted any item yet.", "creator",
                         only_published=False)

@login_required
def searches(request):
    page_title = u"My Saved Searches"
    breadcrumbs = [
        {"url": reverse("myitems:myitems"), "title": u"My Items"},
        {"url": reverse("myitems:searches"), "title": page_title},
    ]

    items = list(SavedSearch.objects.filter(user=request.user))
    for item in items:
        item.unsave_item_url = reverse("savedsearches:unsave", kwargs=dict(id=item.id))

    return direct_to_template(request, "myitems/searches.html", locals())



class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ("name", )
        widgets = { "name": forms.TextInput(), }



class FolderCreate(CreateView):
    form_class = FolderForm
    template_name = "myitems/include/folder-create.html"


    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(FolderCreate, self).get(request, *args, **kwargs)


    @method_decorator(login_required)
    @method_decorator(ajax_request)
    def post(self, request, *args, **kwargs):
        return super(FolderCreate, self).post(request, *args, **kwargs)


    def get_form(self, form_class):
        form = super(FolderCreate,self).get_form(form_class)
        form.instance = Folder(user=self.request.user)
        return form


    def form_valid(self, form):
        return { "status": "success" }


    def form_invalid(self, form):
        return { "status": "error" }