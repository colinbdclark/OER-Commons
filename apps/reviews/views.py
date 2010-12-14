from django import forms
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from haystack.sites import site
from reviews.models import Review
from utils.decorators import login_required
from utils.shortcuts import redirect_to_next_url


class ReviewForm(forms.Form):

    text = forms.CharField(label=u"Review text:",
                     required=False,
                     help_text=u"You can add a review on this item to help others know more about its use or quality.",
                     widget=forms.Textarea(attrs={"class": "text"}))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.user = kwargs.pop("user", None)
        super(ReviewForm, self).__init__(*args, **kwargs)

        if self.instance is not None and self.user is not None:
            try:
                self.fields["text"].initial = self.instance.reviews.get(user=self.user).text
            except Review.DoesNotExist:
                pass

    def save(self):
        if not self.instance or not self.user:
            return
        content_type = ContentType.objects.get_for_model(self.instance)
        object_id = self.instance.id

        text = self.cleaned_data["text"].strip()

        if not text:
            # Delete review
            self.instance.reviews.filter(user=self.user).delete()
        else:
            review, created = Review.objects.get_or_create(
                                            content_type=content_type,
                                            object_id=object_id,
                                            user=self.user)
            review.text = text
            review.save()

        site.update_object(self.instance)


@login_required
def add(request, slug=None, model=None):

    if not slug or not model:
        raise Http404()

    item = get_object_or_404(model, slug=slug)

    page_title = u"Add Review to \"%s\"" % item
    if hasattr(item, "breadcrumbs"):
        breadcrumbs = item.breadcrumbs()
    else:
        breadcrumbs = []

    breadcrumbs.append({"url": "", "title": page_title})

    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect_to_next_url(request, item.get_absolute_url())
        form = ReviewForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, u"Your review was saved.")
            return redirect_to_next_url(request, item.get_absolute_url())
        else:
            messages.error(request, u"Please correct the indicated errors.")
    else:
        form = ReviewForm(instance=item, user=request.user)

    form_action = reverse("materials:%s:add_review" % item.namespace,
                           kwargs=dict(slug=item.slug))

    return direct_to_template(request, "reviews/add.html", locals())
