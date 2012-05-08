from authoring.models import AuthoredMaterial
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from utils.decorators import login_required


class Copy(SingleObjectMixin, View):

    model = AuthoredMaterial

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        object = self.get_object()
        user = request.user
        if user == object.author:
            redirect(object.get_full_url())
        material = object.make_copy(user)
        messages.success(request, u'"%s" was copied.' % object.title)
        return redirect(material.get_edit_url())
