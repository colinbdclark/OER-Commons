from django import forms
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.sites import site
from materials.utils import get_name_from_slug
from tags.models import Tag
from utils.decorators import login_required
from utils.shortcuts import redirect_to_next_url


class TagsField(forms.Field):

    def prepare_value(self, value):
        return u"\n".join(value)

    def to_python(self, value):
        if not value:
            return []

        # Split tags by newline
        tags = [t.strip() for t in value.split("\n") if t.strip()]

        # Split tags by comma
        new_tags = []
        for tag in tags:
            new_tags += [t.strip() for t in tag.split(",") if t.strip()]
        tags = new_tags

        return sorted(set(tags))


class TagsForm(forms.Form):

    tags = TagsField(label=u"Your Tags",
                     required=False,
                     help_text=u"Put each tag on its own line.",
                     widget=forms.Textarea(attrs={"class": "text"}))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.user = kwargs.pop("user", None)
        super(TagsForm, self).__init__(*args, **kwargs)

        if self.instance is not None and self.user is not None:
            self.fields["tags"].initial = sorted(self.instance.tags.filter(user=self.user).values_list("name", flat=True))

    def save(self):
        if not self.instance or not self.user:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id
        existing_tags = Tag.objects.filter(user=self.user,
                                           content_type=content_type,
                                           object_id=object_id)
        # Delete tags
        existing_tags.exclude(name__in=self.cleaned_data["tags"]).delete()

        existing_tag_names = existing_tags.values_list("name", flat=True)
        for tag in self.cleaned_data["tags"]:
            if tag not in existing_tag_names:
                Tag(content_type=content_type, object_id=object_id,
                    user=self.user, name=tag).save()

        site.update_object(self.instance)


@login_required
def add(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    page_title = u"Add Tags to \"%s\"" % item
    if hasattr(item, "breadcrumbs"):
        breadcrumbs = item.breadcrumbs()
    else:
        breadcrumbs = []

    breadcrumbs.append({"url": "", "title": page_title})

    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect_to_next_url(request, item.get_absolute_url())
        form = TagsForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, u"Your tags were saved.")
            return redirect_to_next_url(request, item.get_absolute_url())
        else:
            messages.error(request, u"Please correct the indicated errors.")
    else:
        form = TagsForm(instance=item, user=request.user)

    content_type = ContentType.objects.get_for_model(item)
    object_id = item.id
    user_tags = list(Tag.objects.filter(content_type=content_type,
                                   object_id=object_id,
                                   user=request.user).values_list("slug", flat=True))

    item_tags = list(Tag.objects.filter(content_type=content_type,
                object_id=object_id).exclude(slug__in=user_tags).values_list("slug", flat=True).order_by("slug").distinct())

    all_tags = list(Tag.objects.exclude(slug__in=(user_tags + item_tags)).values_list("slug", flat=True).order_by("slug").distinct())

    item_tags = [get_name_from_slug(Tag, slug) for slug in item_tags]
    all_tags = [get_name_from_slug(Tag, slug) for slug in all_tags]

    form_action = reverse("materials:%s:add_tags" % item.namespace,
                           kwargs=dict(slug=item.slug))

    return direct_to_template(request, "tags/add.html", locals())
