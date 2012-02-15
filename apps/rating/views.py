from annoying.decorators import ajax_request
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from rating import get_rating_stars_class
from rating.models import RATING_VALUES, Rating
from utils.decorators import login_required
from core.search import reindex


class RatingForm(forms.Form):

    number = forms.ChoiceField(list(RATING_VALUES))
    identifier = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(RatingForm, self).__init__(*args, **kwargs)

    def clean_identifier(self):
        identifier = self.cleaned_data["identifier"]
        try:
            app_label, model, object_id = identifier.split(".")
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            model = content_type.model_class()
            self.instance = model.objects.get(id=int(object_id))
        except:
            raise forms.ValidationError(u"Invalid object identifier.")
        return identifier

    def save(self):
        if not self.instance or not self.user:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id

        rating = self.cleaned_data["number"].strip()

        if rating == "delete":
            # Delete rating
            self.instance.ratings.filter(user=self.user).delete()
        else:
            try:
                rating_obj = Rating.objects.get(
                    content_type=content_type,
                    object_id=object_id,
                    user=self.user
                )
                rating_obj.value = int(rating)
                rating_obj.save()
            except Rating.DoesNotExist:
                rating_obj = Rating(content_type=content_type,
                                    object_id=object_id,
                                    user=self.user,
                                    value=int(rating))
                rating_obj.save()

        reindex(self.instance)


@login_required
@ajax_request
def rate(request):

    if not request.is_ajax():
        raise Http404()

    form = RatingForm(request.REQUEST, user=request.user)

    if form.is_valid():
        form.save()
        return dict(status="success",
                    stars_class=get_rating_stars_class(form.instance.rating),
                    message=u"Your rating was saved.")
    else:
        print "!!!", form.errors
        return dict(status="error",
                    message=u"There was a problem with saving your rate.")
