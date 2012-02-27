from annoying.decorators import ajax_request
from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from utils.decorators import login_required


class MaterialViewMixin(SingleObjectMixin):

    model = AuthoredMaterial

    def get_context_data(self, **kwargs):
        data = super(MaterialViewMixin, self).get_context_data(**kwargs)
        data["hide_getsatisfaction"] = True
        return data


class EditMaterialViewMixin(MaterialViewMixin):

    model = AuthoredMaterialDraft
    context_object_name = "object"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #noinspection PyUnresolvedReferences
        return super(EditMaterialViewMixin, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):

        #noinspection PyUnresolvedReferences
        kwargs = dict(
            pk=self.kwargs["pk"]
        )
        #noinspection PyUnresolvedReferences
        user = self.request.user
        if not user.is_superuser and not user.is_staff:
            kwargs["author"] = user
            # TODO: or user in owners

        material = get_object_or_404(
            AuthoredMaterial,
            **kwargs
        )

        draft = material.get_draft()
        return draft


class EditMaterialProcessForm(EditMaterialViewMixin, View):

    form_class = None

    #noinspection PyUnusedLocal
    @ajax_request
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("Only AJAX requests are supported.")
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        return dict(
            status="success"
        )

    def form_invalid(self, form):
        errors = {}
        for field, errors_list in form.errors.items():
            errors[field] = u"<br>".join(errors_list)
        return dict(
            status="error",
            errors=errors,
        )
