from api.decorators import api_method
from api.shortcuts import api_response
from api.utils import get_object
from django.contrib.contenttypes.models import ContentType
from oauth_provider.decorators import oauth_required
from tags.models import Tag


@oauth_required
@api_method
def get_tags(request):

    obj = get_object(request.REQUEST.get("id", None))

    tags = Tag.objects.filter(user=request.user,
                              content_type=ContentType.objects.get_for_model(obj),
                              object_id=obj.id).values_list("name", flat=True)

    return api_response(dict(tags=list(tags)))
