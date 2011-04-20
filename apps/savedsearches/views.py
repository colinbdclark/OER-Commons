from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from savedsearches.models import SavedSearch
from utils.decorators import login_required
from utils.shortcuts import redirect_to_next_url
from annoying.decorators import JsonResponse


class SaveSearchForm(forms.Form):

    url = forms.CharField(widget=forms.HiddenInput())

    title = forms.CharField(label=u"Enter the title for this search",
                            widget=forms.TextInput(attrs={"class": "text"}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(SaveSearchForm, self).__init__(*args, **kwargs)

    def save(self):
        if not self.user:
            return

        SavedSearch.objects.get_or_create(url=self.cleaned_data["url"],
                                          title=self.cleaned_data["title"],
                                          user=self.user)

@login_required
def save(request):

    if "cancel" in request.REQUEST:
        return redirect_to_next_url(request)

    form = SaveSearchForm(request.REQUEST, user=request.user)
    if form.is_valid():
        form.save()
        if request.is_ajax():
            return JsonResponse(dict(message=u"The search was saved."))
        else:
            messages.success(request, u"The search was saved.")

    return redirect_to_next_url(request)

@login_required
def unsave(request, id=None):

    if id is None:
        raise Http404()

    search = get_object_or_404(SavedSearch, id=int(id), user=request.user)

    search.delete()

    if request.is_ajax():
        return JsonResponse(dict(message=u"Saved search was removed."))
    else:
        return redirect_to_next_url(request, reverse("myitems:searches"))
