from api import APIError
from django.contrib.contenttypes.models import ContentType


def get_object(id):

    if not id:
        raise APIError(u"'id' must be specified")

    try:
        app_label, model, id = id.split(".")
        id = int(id)
        content_type = ContentType.objects.get(app_label=app_label,
                                               model=model)
        model = content_type.model_class()
    except:
        raise APIError(u"Invalid 'id'")

    try:
        obj = model.objects.get(id=id)
    except model.DoesNotExist:
        raise APIError(u"Object with gived 'id' does not exist.")

    return obj
