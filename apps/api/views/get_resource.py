from annoying.decorators import ajax_request
from api import APIError
from api.decorators import api_method
from django.contrib.contenttypes.models import ContentType
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from materials.models.material import PUBLISHED_STATE


@api_method
@ajax_request
def get_resource(request):

    url = request.REQUEST.get("url")
    if not url:
        raise APIError("You must specify the URL of resource.")

    object = None
    try:
        object = Course.objects.get(url=url)
    except Course.DoesNotExist:
        raise

    if not object:
        try:
            object = Library.objects.get(url=url)
        except Library.DoesNotExist:
            pass

    if not object:
        try:
            object = CommunityItem.objects.get(url=url)
        except CommunityItem.DoesNotExist:
            pass

    if not object or object.workflow_state != PUBLISHED_STATE:
        raise APIError("Resource with given URL does not exist.")

    content_type = ContentType.objects.get_for_model(object)
    item = {}
    item["id"] = "%s.%s.%i" % (content_type.app_label,
                               content_type.model,
                               object.id)
    item["title"] = object.title
    item["abstract"] = object.abstract
    item["url"] = object.url
    item["keywords"] = object.keyword_names()
    item["subject"] = list(object.general_subjects.all().values_list("name", flat=True))
    item["grade_level"] = list(object.grade_levels.all().values_list("name", flat=True))
    item["collection"] = object.collection and object.collection.name or u""

    return item

