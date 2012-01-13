from authoring.models import AuthoredMaterial
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from utils.decorators import login_required


class New(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        material, created = AuthoredMaterial.objects.get_or_create(
            author=request.user,
            is_new=True
        )
        return redirect("authoring:edit", material_id=material.id)
