from django import forms
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rating import get_rating_stars_class
from rating.models import RATING_VALUES, Rating
from utils.decorators import login_required
from utils.shortcuts import redirect_to_next_url
import cjson
from haystack.sites import site


class RatingForm(forms.Form):

    rating = forms.ChoiceField(choices=([(u"delete", u"--")] + list(RATING_VALUES)))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.user = kwargs.pop("user", None)
        super(RatingForm, self).__init__(*args, **kwargs)

    def save(self):
        if not self.instance or not self.user:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id

        rating = self.cleaned_data["rating"].strip()

        if rating == "delete":
            # Delete rating
            self.instance.ratings.filter(user=self.user).delete()
        else:
            try:
                rating_obj = Rating.objects.get(content_type=content_type,
                                                   object_id=object_id,
                                                   user=self.user)
                rating_obj.value = int(rating)
                rating_obj.save()
            except Rating.DoesNotExist:
                rating_obj = Rating(content_type=content_type,
                                    object_id=object_id,
                                    user=self.user,
                                    value=int(rating))
                rating_obj.save()

        site.update_object(self.instance)



@login_required
def rate(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    form = RatingForm(request.REQUEST, instance=item, user=request.user)

    if form.is_valid():
        form.save()
        if request.method == "POST":
            return HttpResponse(cjson.encode(dict(
                              stars_class=get_rating_stars_class(item.rating),
                              message=u"Your rating was saved."
                              )), content_type="application/json")
        else:
            messages.success(request, u"Your rating was saved.")
    elif request.method == "POST":
        return HttpResponse(cjson.encode(dict(
                          stars_class=get_rating_stars_class(item.rating),
                          message=u"There was a problem with saved your rate."
                          )), content_type="application/json")

    return redirect_to_next_url(request, item.get_absolute_url())
