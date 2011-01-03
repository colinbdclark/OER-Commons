from django.views.generic.simple import direct_to_template
from haystack.query import SearchQuerySet
from materials.models.material import PUBLISHED_STATE
from materials.views.index import IndexParams, populate_item_from_search_result, \
    Pagination
from utils.decorators import login_required
from savedsearches.models import SavedSearch
from django.core.urlresolvers import reverse


def myitems_index(request, view_name, page_title, index_name,
                  only_published=True, template="myitems/index.html"):

    breadcrumbs = [
        {"url": "myitems:myitems", "title": u"My Items"},
        {"url": "myitems:%s" % view_name, "title": page_title},
    ]

    query_string_params = {}
    index_params = IndexParams(request)
    query_string_params = index_params.update_query_string_params(query_string_params)

    batch_end = index_params.batch_start + index_params.batch_size

    query = SearchQuerySet()
    if only_published:
        query = query.narrow("workflow_state:%s" % PUBLISHED_STATE)
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
    return myitems_index(request, "myitems", u"My Saved Items", "saved_by",
                         template="myitems/saved.html")


@login_required
def rated(request):
    return myitems_index(request, "rated", u"My Rated Items", "rated_by")


@login_required
def tagged(request):
    return myitems_index(request, "tagged", u"My Tagged Items", "tagged_by")


@login_required
def reviewed(request):
    return myitems_index(request, "reviewed", u"My Reviewed Items", "reviewed_by")


@login_required
def noted(request):
    return myitems_index(request, "noted", u"My Noted Items", "noted_by")


@login_required
def submitted(request):
    return myitems_index(request, "submitted", u"My Submitted Items", "creator",
                         only_published=False)

@login_required
def searches(request):
    page_title = u"My Saved Searches"
    breadcrumbs = [
        {"url": "myitems:myitems", "title": u"My Items"},
        {"url": "myitems:searches", "title": page_title},
    ]

    items = list(SavedSearch.objects.filter(user=request.user))
    for item in items:
        item.unsave_item_url = reverse("savedsearches:unsave", kwargs=dict(id=item.id))

    return direct_to_template(request, "myitems/searches.html", locals())