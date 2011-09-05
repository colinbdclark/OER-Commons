from annoying.decorators import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from oer.models import Section
from oer.views import OERViewMixin
from utils.decorators import login_required
from utils.views import BaseViewMixin


class Outline(OERViewMixin, BaseViewMixin, TemplateView):

    template_name = "oer/authoring/outline.html"
    restrict_to_owner = True

    page_title = u"Outline"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Outline, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.oer.sections.all().exists():
            Section.objects.create(oer=self.oer)
        return super(Outline, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            if "add-section" in request.POST:
                section = Section.objects.create(oer=self.oer)
                return JsonResponse(dict(status="success", id=section.id))

            elif "delete-section" in request.POST:
                try:
                    Section.objects.get(oer=self.oer, id=int(request.POST["id"])).delete()
                except (ValueError, TypeError, KeyError, Section.DoesNotExist):
                    return JsonResponse(dict(status="error"))
                return JsonResponse(dict(status="success"))

        titles = request.POST.getlist("title")
        ids = request.POST.getlist("id")
        assert len(titles) == len(ids)

        saved = False
        for i, title in enumerate(titles):
            id = int(ids[i])
            order = i+1
            try:
                section = self.oer.sections.get(id=id)
                if section.title != title or section.order != order:
                    section.title = title
                    section.order = order
                    section.save()
                    saved = True
            except Section.DoesNotExist:
                continue

        if request.is_ajax():
            if saved:
                return JsonResponse(dict(status="success", message=u"Changes were saved."))
            return JsonResponse(dict(message=u"Nothing changed."))

        if self.oer.sections.exists() and self.oer.sections.all()[0].title.strip():
            return redirect("oer:edit_add_content", oer_id=self.oer.id,
                            section_number=1)

        return self.get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(Outline, self).get_context_data(*args, **kwargs)
        data["step_number"] = 3
        return data
