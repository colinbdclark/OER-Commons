from authoring.models import AuthoredMaterial
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from utils.decorators import login_required


class New(View):

    #noinspection PyUnusedLocal
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        material = AuthoredMaterial.objects.create(
            author=request.user,
            is_new=True
        )
        return redirect("authoring:edit", pk=material.pk)
