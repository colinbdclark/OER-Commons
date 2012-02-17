from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.detail import SingleObjectMixin
from utils.decorators import login_required


class MaterialViewMixin(SingleObjectMixin):

    model = AuthoredMaterial


class EditMaterialViewMixin(MaterialViewMixin):

    model = AuthoredMaterialDraft

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #noinspection PyUnresolvedReferences
        return super(EditMaterialViewMixin, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):

        #noinspection PyUnresolvedReferences
        material = get_object_or_404(
            AuthoredMaterial,
            author=self.request.user, # TODO: or request.user in owners
            pk=self.kwargs["pk"],
        )

        draft = material.get_draft()
        return draft
