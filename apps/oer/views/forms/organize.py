from annoying.decorators import JsonResponse
from common.models import Keyword
from curriculum.models import TaggedMaterial
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from oer.models import OER, Group
from oer.views import OERViewMixin
from sorl.thumbnail import delete
from utils.decorators import login_required
from utils.forms import AutocompleteListField, AutocompleteListWidget
from utils.views import BaseViewMixin
import json
import time


class OrganizeForm(forms.ModelForm):

    group = forms.ModelChoiceField(Group.objects.all(),
                label=u"Add to an item group",
                help_text=u"and keep your items straight",
                empty_label=u"Select Item Group",
                required=False,
                )

    instruction_date = forms.DateField(
                label=u"Choose a date of instruction?",
                help_text=u"we'll put it in your calendar in 'My Items'",
                widget=forms.DateInput(attrs={"placeholder": "MM/DD/YYYY"},
                                       format="%m/%d/%Y"),
                input_formats=["%m/%d/%Y"],
                required=False,
                )

    keywords = AutocompleteListField(model=Keyword,
                                     label=u"Tag with keywords or subjects",
                                     help_text=u"to help others find your resource",
                                     required=False,
                                     widget=AutocompleteListWidget(use_placeholder_label=True))


    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(OrganizeForm, self).__init__(*args, **kwargs)
        self.fields["group"].queryset = self.fields["group"].queryset.filter(user=user)

    class Meta:
        model = OER
        fields = ["group", "instruction_date", "keywords"]


class Organize(OERViewMixin, BaseViewMixin, TemplateView):

    template_name = "oer/authoring/organize.html"
    restrict_to_owner = True

    page_title = u"Organize OER"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Organize, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if getattr(self, "form", None) is None:
            self.form = OrganizeForm(instance=self.oer, user=request.user)
        return super(Organize, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = OrganizeForm(request.POST, instance=self.oer,
                                 user=request.user)
        if self.form.is_valid():
            self.form.save()
            if request.is_ajax():
                return JsonResponse(dict(status="success", message=u"Changes were saved."))
        else:
            if request.is_ajax():
                errors = {}
                for field_name, errors_list in self.form.errors.items():
                    errors[field_name] = errors_list[0]
                return JsonResponse(dict(status="error", errors=errors))

        return self.get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(Organize, self).get_context_data(*args, **kwargs)
        data["form"] = self.form
        data["step_number"] = 2
        align_user_tags = []
        content_type = ContentType.objects.get_for_model(self.oer)
        for tagged in TaggedMaterial.objects.filter(content_type=content_type,
                                                    object_id=self.oer.id,
                                                    user=self.request.user).select_related():
            align_user_tags.append(tagged)
        data["align_user_tags"] = align_user_tags
        return data


class ImageForm(forms.Form):

    file = forms.FileField()


class Image(OERViewMixin, View):

    restrict_to_owner = True
    action = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Image, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.action == "upload":
            form = ImageForm(request.POST, request.FILES)
            response = dict(status="error", message=u"")
            if form.is_valid():
                if self.oer.image:
                    delete(self.oer.image)
                image = form.cleaned_data["file"]
                if image.content_type == "image/jpeg":
                    extension = ".jpg"
                elif image.content_type == "image/png":
                    extension = ".png"
                elif image.content_type == "image/gif":
                    extension = ".gif"
                else:
                    extension = ""
                filename = "%i%s" % (self.oer.id, extension)
                self.oer.image.save(filename, image)
                response["status"] = "success"
                response["message"] = u"Your picture is saved."
                response["url"] = self.oer.get_thumbnail().url + "?" + str(int(time.time()))
            else:
                response["message"] = form.errors["file"][0]
            # We don't use application/json content type here because IE misinterprets it.
            return HttpResponse(json.dumps(response))
        elif self.action == "remove":
            if self.oer.image:
                delete(self.oer.image)
                self.oer.image = None
                self.oer.save()
            return JsonResponse(dict(status="success",
                                     message=u"Image was removed."))
        raise Http404()
