from annoying.decorators import ajax_request
from annoying.functions import get_object_or_None
from api.decorators import api_method
from api.utils import get_object
from django.contrib.contenttypes.models import ContentType
from oauth_provider.decorators import oauth_required
from reviews.models import Review
from reviews.views import ReviewForm


@oauth_required
@api_method
@ajax_request
def set_review(request):

    obj = get_object(request.REQUEST.get("id", None))

    content_type = ContentType.objects.get_for_model(obj)

    Review.objects.get_or_create()
    review = get_object_or_None(Review,
        content_type=content_type,
        object_id=obj.id,
        user=request.user,
    ) or Review(
        content_type=content_type,
        object_id=obj.id,
        user=request.user,
    )

    form = ReviewForm(request.REQUEST,
                      instance=review)

    if form.is_valid():
        form.save()
        return dict(status="success")
    else:
        return dict(errors=form._errors)
