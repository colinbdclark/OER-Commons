from django.db.models.aggregates import Avg
from django.template import Library
from rating import get_rating_stars_class


register = Library()


@register.inclusion_tag("rating/include/stars.html")
def stars(identifier, value):
    if isinstance(value, float):
        return {"class":get_rating_stars_class(value),
                "identifier": identifier}
    else:
        ratings = value
        count = ratings.count() 
        value = 0.0
        if count:
            value = ratings.aggregate(rating=Avg("value"))["rating"]

        return {"class":get_rating_stars_class(value),
                "rating_value": "%0.1f" % value,
                "rating_count": count,
                "identifier": identifier}
        
