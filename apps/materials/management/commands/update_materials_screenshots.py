from optparse import make_option
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from materials.models import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from materials.tasks import update_screenshot, check_url_status
import pprocess
import traceback


class Processor(pprocess.Exchange):

    def store_data(self, ch):
        result = ch.receive()
        self.cnt += 1
        print "%i of %i..." % (self.cnt, self.total_items)


class Command(BaseCommand):

    help = u"Update materials screenshots."
    option_list = BaseCommand.option_list + (
            make_option('--workers',
                action='store',
                type='int',
                dest='workers_number',
                default=5,
                help='A number of parallel processes used to make screenshots. Default: 5'),
            make_option('--update-existing',
                action='store_true',
                dest='update_existing',
                default=False,
                help='Update existing screenshots.'),
            )

    def handle(self, **options):

        content_types = {}

        models = [Course, Library, CommunityItem]

        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            content_types[content_type.id] = content_type

        filters = dict(http_status__in=(None, 200))
        if not options["update_existing"]:
            filters["screenshot"] = None

        total_items = sum([model.objects.filter(**filters).count() for model in models])

        def process_item(content_types, content_type_id, object_id):
            content_type = content_types[content_type_id]
            model = content_type.model_class()
            try:
                item = None
                try:
                    item = model.objects.get(pk=object_id)
                except model.DoesNotExist:
                    pass
                if item:
                    item._post_save_processed = True
                    if not item.http_status:
                        check_url_status(item)
                    update_screenshot(item)
            except:
                if settings.DEBUG:
                    print "Exception while processing %s %i" % (content_type, object_id)
                    print traceback.format_exc()
            return 1


        processor = Processor(limit=options["workers_number"], reuse=1)
        processor.total_items = total_items
        processor.cnt = 0

        process = processor.manage(pprocess.MakeReusable(process_item))

        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            for object_id in model.objects.filter(**filters).values_list("id", flat=True):
                process(content_types, content_type.id, object_id)

        processor.finish()

        print "Done!"

