from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from oer.models import OER


class OERViewMixin(object):

    restrict_to_owner = False

    def dispatch(self, request, *args, **kwargs):
        self.oer = get_object_or_404(OER, id=int(kwargs["oer_id"]))
        user = request.user
        if self.restrict_to_owner and user != self.oer.author:
            return HttpResponseForbidden()
        return super(OERViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(OERViewMixin, self).get_context_data(*args, **kwargs) or {}
        data["oer"] = self.oer
        return data