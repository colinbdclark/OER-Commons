from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import cjson


MAX_RESULTS = 10


def autocomplete(request, app_label, model, field):
    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    model = content_type.model_class()

    results = []
    term = request.REQUEST.get("term", u"").strip()
    if term and len(term) >= 2:
        try:
            kwargs = {"%s__istartswith" % field: term}
            results = list(model.objects.filter(**kwargs).values_list(field, flat=True).distinct().order_by(field)[:MAX_RESULTS])
            if len(results) < MAX_RESULTS:
                kwargs = {"%s__icontains" % field: term}
                exclude_kwargs = {"%s__in" % field: results}
                results += list(model.objects.filter(**kwargs).exclude(**exclude_kwargs).values_list(field, flat=True).distinct().order_by(field)[:MAX_RESULTS - len(results)])
        except:
            pass

    return HttpResponse(cjson.encode(results), "application/json")
