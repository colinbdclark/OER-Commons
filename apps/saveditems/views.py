from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from annoying.decorators import ajax_request
from saveditems.models import SavedItem
from utils.decorators import login_required
from core.search import reindex


@login_required
@ajax_request
def save(request):
    content_type_id, object_id = request.POST["identifier"].split(".")

    content_type = get_object_or_404(ContentType, id=content_type_id)
    item = get_object_or_404(content_type.model_class(), id=object_id)
    SavedItem.objects.get_or_create(content_type=content_type,
                          object_id=object_id,
                          user=request.user)
    reindex(item)

    return dict(status="success",
                message=u"Item was saved in your collection.")


@login_required
@ajax_request
def unsave(request):
    content_type_id, object_id = request.POST["identifier"].split(".")

    content_type = get_object_or_404(ContentType, id=content_type_id)
    item = get_object_or_404(content_type.model_class(), id=object_id)
    try:
        SavedItem.objects.get(content_type=content_type,
                              object_id=object_id,
                              user=request.user).delete()

        reindex(item)
    except SavedItem.DoesNotExist:
        pass

    return dict(status="success",
                message=u"Item was removed from your collection.")
