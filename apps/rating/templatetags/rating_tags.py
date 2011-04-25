from django.template import Library
from rating import get_rating_stars_class


register = Library()


@register.inclusion_tag("rating/include/stars.html")
def stars(rating):
    return {"class":get_rating_stars_class(rating)}
