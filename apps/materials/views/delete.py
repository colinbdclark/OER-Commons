from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template, redirect_to
from utils.decorators import login_required


@login_required
def delete(request, slug=None, model=None):

    item = get_object_or_404(model, slug=slug)
    page_title = u"Delete \"%s\"" % item.title
    breadcrumbs = [
       {"url": model.get_parent_url(), "title": model._meta.verbose_name_plural},
       {"url": reverse("materials:%s:delete" % model.namespace, kwargs=dict(slug=slug)), "title": page_title}
    ]

    if item.creator != request.user and not request.user.is_staff:
        raise Http404()

    if request.method == "POST":
        if "delete" in request.POST:
            title = item.title
            item.delete()
            messages.success(request, u"\"%s\" was removed." % title)
            return redirect_to(request, model.get_parent_url(), permanent=False)
        elif "cancel" in request.POST:
            return redirect(item)

    return direct_to_template(request, "materials/delete.html", locals())
