from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
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

