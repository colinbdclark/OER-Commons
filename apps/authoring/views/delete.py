from authoring.models import AuthoredMaterial, AuthoredMaterialDraft
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from utils.decorators import login_required


class Delete(SingleObjectMixin, View):

    model = AuthoredMaterial

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        object = self.get_object()
        user = request.user
        # TODO: or user in owners
        if not user.is_superuser and not user.is_staff and not user == object.author:
            return HttpResponseForbidden()
        title = object.title
        if title:
            messages.success(request, u'"%s" was deleted.' % title)
        else:
            messages.success(request, u'The material was deleted.')
        object.delete()
        return redirect("myitems:myitems")


class DeleteDraft(SingleObjectMixin, View):

    model = AuthoredMaterialDraft

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        object = self.get_object()
        user = request.user
        # TODO: or user in owners
        if not user.is_superuser and not user.is_staff and not user == object.material.author:
            return HttpResponseForbidden()
        if object.material.is_new:
            messages.success(request, u'The draft was deleted.')
        else:
            messages.success(request, u'The unpublished changes for "%s" were deleted.' % object.material.title)
        object.delete()
        return redirect("myitems:myitems")
