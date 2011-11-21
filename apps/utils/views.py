from annoying.decorators import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404


class BaseViewMixin(object):

    page_title = u""
    def get_page_title(self):
        return self.page_title

    page_subtitle = u""
    def get_page_subtitle(self):
        return self.page_subtitle

    breadcrumbs = []
    def get_breadcrumbs(self):
        return self.breadcrumbs

    hide_global_notifications = False
    def get_hide_global_notifications(self):
        return self.hide_global_notifications

    def get_context_data(self, *args, **kwargs):
        data = super(BaseViewMixin, self).get_context_data(*args, **kwargs)
        data["page_title"] = self.get_page_title()
        data["page_subtitle"] = self.get_page_subtitle()
        data["breadcrumbs"] = self.get_breadcrumbs()
        data["hide_global_notifications"] = self.get_hide_global_notifications()
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
