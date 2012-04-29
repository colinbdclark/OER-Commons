from authoring.views import MaterialViewMixin
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from utils.decorators import login_required


class Delete(MaterialViewMixin, View):

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
