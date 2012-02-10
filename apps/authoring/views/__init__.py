from authoring.models import AuthoredMaterial
from django.utils.decorators import method_decorator
from django.views.generic.detail import SingleObjectMixin
from utils.decorators import login_required


class MaterialViewMixin(SingleObjectMixin):

    model = AuthoredMaterial


class EditMaterialViewMixin(MaterialViewMixin):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #noinspection PyUnresolvedReferences
        return super(EditMaterialViewMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(EditMaterialViewMixin, self).get_queryset()
        #noinspection PyUnresolvedReferences
        return qs.filter(author=self.request.user)
