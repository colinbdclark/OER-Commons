from annoying.decorators import JsonResponse
from authoring.models import AuthoredMaterial
from authoring.views import EditMaterialViewMixin
from authoring.views.forms import EditForm
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import UpdateView


class Edit(EditMaterialViewMixin, UpdateView):

    form_class = EditForm
    template_name = "authoring/edit.html"

    def get_form_kwargs(self):
        kwargs = super(Edit, self).get_form_kwargs()
        if self.request.is_ajax() or "preview" in self.request.GET:
            kwargs["not_required"] = True
        kwargs["hide_submit_step"] = self.object.material.published and self.object.material.license
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(Edit, self).get_context_data(**kwargs)
        data["hide_submit_step"] = self.object.material.published and self.object.material.license
        return data

    def form_valid(self, form):
        self.object = form.save()
        if "preview" in self.request.GET:
            return redirect(self.object.get_absolute_url())
        if self.request.is_ajax():
            return JsonResponse(dict(
                status="success",
                message=u"Saved."
            ))
        material = AuthoredMaterial.publish_draft(self.object)
        return redirect(material.get_absolute_url())

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors = {}
            for field, errors_list in form.errors.items():
                errors[field] = u"<br>".join(errors_list)
            return JsonResponse(dict(
                status="error",
                message=u"Please correct the indicated errors.",
                errors=errors,
            ))
        if "title" in form.errors:
            messages.error(self.request, u"Please enter a title.")
        else:
            messages.error(self.request, u"Please correct the indicated errors.",)
        return super(Edit, self).form_invalid(form)
