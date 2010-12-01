from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404


@login_required
def add(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    return None
