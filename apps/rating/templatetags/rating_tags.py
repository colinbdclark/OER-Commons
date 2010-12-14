from django.template import Library
from rating import get_rating_stars_class
from rating.models import RATING_VALUES
from rating.views import RatingForm


register = Library()


@register.inclusion_tag("rating/include/rate-form.html", takes_context=True)
def rate_form(context, form_action=u""):
    request = context.get("request", None)
    form_method = "get"
    if request is not None:
        if request.user.is_authenticated():
            form_method = "post"
    form = RatingForm()
    return dict(form=form, form_action=form_action, form_method=form_method,
                request=request)


@register.inclusion_tag("rating/include/stars.html")
def stars(rating):
    return {"class":get_rating_stars_class(rating)}
