from annoying.decorators import ajax_request
from api.decorators import api_method
from api.utils import get_object
from django import forms
from django.contrib.contenttypes.models import ContentType
from haystack.sites import site
from oauth_provider.decorators import oauth_required
from tags.models import Tag


class TagsField(forms.Field):

    def prepare_value(self, value):
        return u", ".join(value)

    def to_python(self, value):
        if not value:
            return []

        # Split tags by comma
        tags = [t.strip() for t in value.split(",") if t.strip()]
        return sorted(set(tags))


class TagsForm(forms.Form):

    tags = TagsField(required=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.user = kwargs.pop("user", None)
        super(TagsForm, self).__init__(*args, **kwargs)

    def save(self):
        if not self.instance or not self.user:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id
        existing_tags = Tag.objects.filter(user=self.user,
                                           content_type=content_type,
                                           object_id=object_id)
        
        existing_tag_names = existing_tags.values_list("name", flat=True)
        for tag in self.cleaned_data["tags"]:
            if tag not in existing_tag_names:
                Tag(content_type=content_type, object_id=object_id,
                    user=self.user, name=tag).save()

        site.update_object(self.instance)


@oauth_required
@api_method
@ajax_request
def set_tags(request):

    obj = get_object(request.REQUEST.get("id", None))

    form = TagsForm(request.REQUEST,
                    instance=obj,
                    user=request.user)

    if form.is_valid():
        form.save()
        return dict(status="success")
    else:
        return dict(errors=form._errors)
