from api.decorators import api_method
from api.shortcuts import api_response
from api.utils import get_object
from django.contrib.contenttypes.models import ContentType
from oauth_provider.decorators import oauth_required
from reviews.models import Review


@oauth_required
@api_method
def get_review(request):

    obj = get_object(request.REQUEST.get("id", None))

    try:
        review = Review.objects.get(content_type=ContentType.objects.get_for_model(obj),
                                    object_id=obj.id,
                                    user=request.user).text
    except Review.DoesNotExist:
        review = None

    return api_response(dict(review=review))
