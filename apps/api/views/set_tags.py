from api.decorators import api_method
from api.shortcuts import api_response
from api.utils import get_object
from oauth_provider.decorators import oauth_required
from tags.views import TagsForm


@oauth_required
@api_method
def set_tags(request):

    obj = get_object(request.REQUEST.get("id", None))

    form = TagsForm(request.REQUEST,
                    instance=obj,
                    user=request.user)

    if form.is_valid():
        form.save()
        return api_response(dict(status="success"))
    else:
        return api_response(dict(errors=form._errors))
