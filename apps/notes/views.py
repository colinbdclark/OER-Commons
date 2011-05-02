from annoying.decorators import JsonResponse
from django import forms
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.sites import site
from notes.models import Note
from saveditems.models import SavedItem
from utils.decorators import login_required
from utils.shortcuts import redirect_to_next_url


class NoteForm(forms.Form):

    text = forms.CharField(label=u"Note:",
                     required=False,
                     widget=forms.Textarea(attrs={"class": "text"}))

    save_item = forms.BooleanField(label=u"Save this item in your collection?",
                                   required=False,
                                   initial=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.user = kwargs.pop("user", None)
        super(NoteForm, self).__init__(*args, **kwargs)

        if self.instance is not None and self.user is not None:
            try:
                self.fields["text"].initial = self.instance.notes.get(user=self.user).text
            except Note.DoesNotExist:
                pass
            if self.instance.saved_items.filter(user=self.user).count():
                self.fields["save_item"].initial = True

    def save(self):
        if not self.instance or not self.user:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id

        text = self.cleaned_data["text"].strip()

        if not text:
            # Delete note
            self.instance.notes.filter(user=self.user).delete()
        else:
            note, created = Note.objects.get_or_create(
                                            content_type=content_type,
                                            object_id=object_id,
                                            user=self.user)
            note.text = text
            note.save()

        if self.cleaned_data["save_item"]:
            SavedItem.objects.get_or_create(content_type=content_type,
                                            object_id=object_id,
                                            user=self.user)
        else:
            self.instance.saved_items.filter(user=self.user).delete()

        site.update_object(self.instance)


@login_required
def add(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    page_title = u"Add Note to \"%s\"" % item
    if hasattr(item, "breadcrumbs"):
        breadcrumbs = item.breadcrumbs()
    else:
        breadcrumbs = []

    breadcrumbs.append({"url": "", "title": page_title})

    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect_to_next_url(request, item.get_absolute_url())
        form = NoteForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return JsonResponse(dict(status="success",
                                         message=u"Your note was saved."))
            else:
                messages.success(request, u"Your note was saved.")
                return redirect_to_next_url(request, item.get_absolute_url())
        else:
            if request.is_ajax():
                errors = {}
                for field, errors_list in form.errors.items():
                    errors[field] = errors_list[0]
                return JsonResponse(dict(status="error",
                                         errors=errors))
            else:
                messages.error(request, u"Please correct the indicated errors.")
    else:
        form = NoteForm(instance=item, user=request.user)

    form_action = reverse("materials:%s:add_note" % item.namespace,
                           kwargs=dict(slug=item.slug))

    return direct_to_template(request, "notes/add.html", locals())
