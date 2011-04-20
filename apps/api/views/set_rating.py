from annoying.decorators import ajax_request
from api.decorators import api_method
from api.utils import get_object
from oauth_provider.decorators import oauth_required
from rating.views import RatingForm


@oauth_required
@api_method
@ajax_request
def set_rating(request):

    obj = get_object(request.REQUEST.get("id", None))

    form = RatingForm(request.REQUEST,
                      instance=obj,
                      user=request.user)

    if form.is_valid():
        form.save()
        return dict(status="success")
    else:
        return dict(errors=form._errors)
