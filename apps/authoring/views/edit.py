from annoying.decorators import JsonResponse
from authoring.models import AuthoredMaterial
from authoring.views import EditMaterialViewMixin
from authoring.views.forms import EditForm, ResubmitForm
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import UpdateView
from materials.models.material import PUBLISHED_STATE


class Edit(EditMaterialViewMixin, UpdateView):

    template_name = "authoring/edit.html"

    def get_form_class(self):
        if self.object.material.workflow_state == PUBLISHED_STATE and self.object.material.license:
            return ResubmitForm
        return EditForm

    def get_form_kwargs(self):
        kwargs = super(Edit, self).get_form_kwargs()
        if self.request.is_ajax() or "preview" in self.request.GET:
            kwargs["not_required"] = True
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(Edit, self).get_context_data(**kwargs)
        data["resubmit"] = self.object.material.workflow_state == PUBLISHED_STATE and self.object.material.license
        return data

    def form_valid(self, form):
        force = self.request.POST.get("force_save")
        if self.request.is_ajax() and not force and self.request.POST.get("checksum") != self.get_object().checksum:
            return JsonResponse(dict(
                status="error",
                message=u"",
                reason="checksum",
            ))
        self.object = form.save()
        if "preview" in self.request.GET:
            return redirect(self.object.get_absolute_url())
        if self.request.is_ajax():
            return JsonResponse(dict(
                status="success",
                message=u"Saved.",
                checksum=self.object.checksum,
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
