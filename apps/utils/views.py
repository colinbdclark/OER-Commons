from annoying.decorators import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404


class OERViewMixin(object):

    def get_page_title(self):
        return None
    page_title = property(get_page_title)

    def get_page_subtitle(self):
        return None
    page_subtitle = property(get_page_subtitle)

    def get_breadcrumbs(self):
        return None
    breadcrumbs = property(get_breadcrumbs)

    def get_context_data(self, *args, **kwargs):
        data = super(OERViewMixin, self).get_context_data(*args, **kwargs)
        data["page_title"] = self.page_title
        data["page_subtitle"] = self.page_subtitle
        data["breadcrumbs"] = self.breadcrumbs
        return data


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

    return JsonResponse(results)
