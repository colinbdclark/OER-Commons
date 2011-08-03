from annoying.decorators import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from oer.models import Chapter
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
        if not self.oer.chapters.all().exists():
            Chapter.objects.create(oer=self.oer)
        return super(Outline, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            if "add-chapter" in request.POST:
                chapter = Chapter.objects.create(oer=self.oer)
                return JsonResponse(dict(status="success", id=chapter.id))

            elif "delete-chapter" in request.POST:
                try:
                    Chapter.objects.get(oer=self.oer, id=int(request.POST["id"])).delete()
                except (ValueError, TypeError, KeyError, Chapter.DoesNotExist):
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
                    chapter = self.oer.chapters.get(id=id)
                    if chapter.title != title or chapter.order != order:
                        chapter.title = title
                        chapter.order = order
                        chapter.save()
                        saved = True
                except Chapter.DoesNotExist:
                    continue

            if saved:
                return JsonResponse(dict(status="success", message=u"Changes were saved."))

            return JsonResponse(dict(message=u"Nothing changed."))


        return self.get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(Outline, self).get_context_data(*args, **kwargs)
        data["step_number"] = 3
        return data
