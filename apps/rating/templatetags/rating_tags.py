from django.template import Library
from rating import get_rating_stars_class
from rating.views import RatingForm


register = Library()


@register.inclusion_tag("rating/include/rate-form.html", takes_context=True)
def rate_form(context, form_action=u""):
    form = RatingForm()
    return dict(form=form, form_action=form_action)


@register.inclusion_tag("rating/include/stars.html")
def stars(rating):
    return {"class":get_rating_stars_class(rating)}
