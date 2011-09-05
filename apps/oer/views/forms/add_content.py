from annoying.decorators import JsonResponse
from django import forms
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from oer.models import Section
from oer.views import OERViewMixin
from utils.decorators import login_required
from utils.views import BaseViewMixin


class AddContentForm(forms.ModelForm):

    title = forms.CharField()

    text = forms.CharField(widget=forms.Textarea())

    class Meta:
        fields = ["title", "text"]
        model = Section


class AddContent(OERViewMixin, BaseViewMixin, TemplateView):

    template_name = "oer/authoring/add-content.html"

    restrict_to_owner = True

    page_title = u"Add Content"

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(AddContent, self).dispatch(request, *args, **kwargs)

    def prepare(self, request, *args, **kwargs):
        sections = self.oer.sections.all()
        self.section_number = int(kwargs["section_number"])
        self.total_sections = sections.count()
        if self.section_number == 0:
            raise Http404()
        try:
            self.section = sections[self.section_number-1]
        except IndexError:
            self.section = None

    def get(self, request, *args, **kwargs):
        self.prepare(request, *args, **kwargs)
        if not self.section:
            return redirect("oer:edit_outline", oer_id=self.oer.id)
        if getattr(self, "form", None) is None:
            self.form = AddContentForm(instance=self.section)
        return super(AddContent, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.prepare(request, *args, **kwargs)
        if not self.section:
            return redirect("oer:edit_outline", oer_id=self.oer.id)
        self.form = AddContentForm(request.POST, instance=self.section)
        if self.form.is_valid():
            self.form.save()
            if request.is_ajax():
                return JsonResponse(dict(status="success", message=u"Changes were saved."))
            else:
                if self.section_number < self.total_sections:
                    return redirect("oer:edit_add_content", oer_id=self.oer.id,
                                    section_number=self.section_number+1)
                else:
                    return redirect("oer:edit_license", oer_id=self.oer.id)
        else:
            if request.is_ajax():
                errors = {}
                for field_name, errors_list in self.form.errors.items():
                    errors[field_name] = errors_list[0]
                return JsonResponse(dict(status="error", errors=errors))

        return self.get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(AddContent, self).get_context_data(*args, **kwargs)
        data["section"] = self.section
        data["section_number"] = self.section_number
        data["prev_section_number"] = None
        data["next_section_number"] = None
        if self.section_number > 1:
            data["prev_section_number"] = self.section_number - 1
        if self.section_number < self.total_sections:
            data["next_section_number"] = self.section_number + 1
        data["form"] = self.form
        data["step_number"] = 4
        return data
