from annoying.decorators import ajax_request
from annoying.functions import get_object_or_None
from api import APIError
from api.decorators import api_method
from django.contrib.contenttypes.models import ContentType
from haystack.query import SearchQuerySet
from materials.models import Course, Library, CommunityItem
from rubrics.models import Rubric


@api_method
@ajax_request
def get_evaluations(request):

    qs = SearchQuerySet().filter(
        evaluated_rubrics__in=[0] + list(Rubric.objects.values_list("id", flat=True))
    ).narrow("is_displayed:true")
    size = int(request.REQUEST.get("size", 100))
    start = int(request.REQUEST.get("start", 0))

    total_items = qs.count()

    items = []

    if start < total_items and start >= 0:
        for r in qs[start:start+size]:
            fields = r.get_stored_fields()
            items.append(dict(
                title=fields["title"],
                url=fields["url"],
                rubric_1=fields["evaluation_score_rubric_0"],
                rubric_2=fields["evaluation_score_rubric_1"],
                rubric_3=fields["evaluation_score_rubric_2"],
                rubric_4=fields["evaluation_score_rubric_3"],
                rubric_5=fields["evaluation_score_rubric_4"],
                rubric_6=fields["evaluation_score_rubric_5"],
                rubric_7=fields["evaluation_score_rubric_6"],
            ))

    return dict(items=items, total_items=total_items)


@api_method
@ajax_request
def get_evaluation(request):

    qs = SearchQuerySet().filter(
        evaluated_rubrics__in=[0] + list(Rubric.objects.values_list("id", flat=True))
    ).narrow("is_displayed:true")

    url = request.REQUEST.get("url")
    if not url:
        raise APIError(u"URL is missing.")

    for model in (Course, Library, CommunityItem):
        obj = get_object_or_None(model, url=url)
        if obj:
            break

    if obj is None:
        raise APIError("Resource with given URL is not registered.")

    qs = qs.models(obj.__class__).narrow("django_id:%i" % obj.id)

    if qs.count():
        fields = qs[0].get_stored_fields()
        item = dict(
            title=fields["title"],
            url=fields["url"],
            rubric_1=fields["evaluation_score_rubric_0"],
            rubric_2=fields["evaluation_score_rubric_1"],
            rubric_3=fields["evaluation_score_rubric_2"],
            rubric_4=fields["evaluation_score_rubric_3"],
            rubric_5=fields["evaluation_score_rubric_4"],
            rubric_6=fields["evaluation_score_rubric_5"],
            rubric_7=fields["evaluation_score_rubric_6"],
        )
        return dict(item=item)

    else:
        raise APIError("Resource with given URL is not evaluated.")

