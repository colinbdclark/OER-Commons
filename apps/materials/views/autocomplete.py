from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import cjson


def autocomplete(request, app_label, model, field):
    content_type = get_object_or_404(ContentType, app_label=app_label,
                                     model=model)
    model = content_type.model_class()
    
    results = []
    term = request.REQUEST.get("term", u"").strip()
    if term and len(term) >= 2:
        try:
            kwargs = {"%s__icontains" % field: term}
            results = model.objects.filter(**kwargs).values_list(field, flat=True).distinct().order_by(field)[:10]
        except:
            pass

    results = [r.encode("utf-8") for r in results]

    return HttpResponse(cjson.encode(results), "application/json") 