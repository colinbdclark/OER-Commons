from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.simple import direct_to_template
from materials.models.community import CommunityItem
from materials.models.material import PRIVATE_STATE
from materials.views.forms.community.add import AddFormStaff
from utils.decorators import login_required


class EditForm(AddFormStaff):

    slug = forms.SlugField(label=u"Short Name:",
                           widget=forms.TextInput(
                           attrs={"class": "text wide"}))

    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        del self.fields["in_rss"]
        del self.fields["rss_description"]
        del self.fields["rss_timestamp"]
        self.fields["slug"].initial = self.instance.slug
        self.set_initial_license_data()

    def clean_slug(self):
        value = self.cleaned_data["slug"]
        instance = getattr(self, "instance", None)
        qs = CommunityItem.objects.filter(slug=value)
        if instance and instance.id:
            qs = qs.exclude(id=instance.id)
        if qs.count():
            raise forms.ValidationError(u"This short name is used by another object.")
        return value

    class Meta:
        model = CommunityItem
        fields = ["slug", "title", "url", "abstract",
                  "content_creation_date", "authors",
                  "tech_requirements", "keywords", "general_subjects",
                  "grade_levels", "languages", "geographic_relevance",
                  "community_topics", "community_types",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_name", "license_custom_url", "license_description",
                  "copyright_holder", "license"]


class EditFormStaff(AddFormStaff):

    slug = forms.SlugField(label=u"Short Name:",
                           widget=forms.TextInput(
                           attrs={"class": "text wide"}))

    def __init__(self, *args, **kwargs):
        super(EditFormStaff, self).__init__(*args, **kwargs)
        self.fields["slug"].initial = self.instance.slug
        self.set_initial_license_data()

    def clean_slug(self):
        value = self.cleaned_data["slug"]
        instance = getattr(self, "instance", None)
        qs = CommunityItem.objects.filter(slug=value)
        if instance and instance.id:
            qs = qs.exclude(id=instance.id)
        if qs.count():
            raise forms.ValidationError(u"This short name is used by another object.")
        return value

    class Meta:
        model = CommunityItem
        fields = ["slug", "title", "url", "abstract",
                  "content_creation_date", "authors",
                  "tech_requirements", "keywords", "general_subjects",
                  "grade_levels", "languages", "geographic_relevance",
                  "community_topics", "community_types",
                  "in_rss", "rss_description", "rss_timestamp",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_name", "license_custom_url", "license_description",
                  "copyright_holder", "license"]


@login_required
def edit(request, slug=None, model=None):

    instance = get_object_or_404(model, slug=slug)

    if instance.creator != request.user and not request.user.is_staff:
        raise Http404()

    if request.user.is_staff:
        form_class = EditFormStaff
        template = "materials/forms/community/edit-staff.html"
    else:
        form_class = EditForm
        template = "materials/forms/community/edit.html"

    page_title = u"Edit \"%s\"" % instance.title
    breadcrumbs = [
        {"url": model.get_parent_url(), "title": model._meta.verbose_name_plural},
        {"url": reverse("materials:community:edit", kwargs=dict(slug=slug)), "title": page_title}
    ]

    if request.method == "POST":
        form = form_class(request.POST, instance=instance)

        if form.is_valid():
            object = form.save(commit=False)
            object.creator = request.user
            object.slug = form.cleaned_data["slug"]
            if not request.user.is_staff:
                object.workflow_state = PRIVATE_STATE
            object.save()
            form.save_m2m()
            messages.success(request, u"Your changes were saved.")
            return redirect(object)
        else:
            messages.error(request, u"Please correct the indicated errors.")
    else:
        form = form_class(instance=instance)

    return direct_to_template(request, template, locals())
