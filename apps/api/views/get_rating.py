from api.decorators import api_method
from api.shortcuts import api_response
from api.utils import get_object
from django.contrib.contenttypes.models import ContentType
from oauth_provider.decorators import oauth_required
from rating.models import Rating


@oauth_required
@api_method
def get_rating(request):

    obj = get_object(request.REQUEST.get("id", None))

    try:
        rating = Rating.objects.get(content_type=ContentType.objects.get_for_model(obj),
                                    object_id=obj.id,
                                    user=request.user).value
    except Rating.DoesNotExist:
        rating = None

    return api_response(dict(rating=rating))
