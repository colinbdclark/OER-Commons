from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from haystack.sites import site
from visitcounts.models import Visit
import datetime


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
        
        
REINDEX_INTERVAL = datetime.timedelta(hours=1)        


class Command(BaseCommand):

    help = u"Reindex visit counts."
    option_list = BaseCommand.option_list

    def handle(self, **options):
        since = datetime.datetime.now() - REINDEX_INTERVAL 
        objects = {}
        for content_type_id, object_id in Visit.objects.filter(timestamp__gte=since).values_list("content_type_id", "object_id"):
            if content_type_id not in objects:
                objects[content_type_id] = [object_id]
            else:
                objects[content_type_id].append(object_id)
        
        for content_type_id, object_ids in objects.items():
            model = ContentType.objects.get(id=content_type_id).model_class()
            index = site.get_index(model)
            for ids in chunks(object_ids, getattr(settings, 'HAYSTACK_BATCH_SIZE', 1000)):
                qs = model.objects.filter(id__in=ids)
                index.backend.update(index, qs)
