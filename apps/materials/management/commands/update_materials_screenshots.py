from optparse import make_option
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from materials.models import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from materials.tasks import update_screenshot, check_url_status
import threading
import Queue


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

        queue = Queue.Queue()

        content_types = {}

        models = [Course, Library, CommunityItem]

        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            content_types[content_type.id] = content_type

        class process(threading.Thread):

            def __init__(self, queue, total_items):
                threading.Thread.__init__(self)
                self.queue = queue
                self.total_items = total_items

            def run(self):
                while True:
                    content_type_id, object_id = self.queue.get()
                    content_type = content_types[content_type_id]
                    model = content_type.model_class()
                    item = None
                    try:
                        item = model.objects.get(pk=object_id)
                    except model.DoesNotExist:
                        self.queue.task_done()
                    if item:
                        item._post_save_processed = True
                        if not item.http_status:
                            check_url_status(item)
                        update_screenshot(item)
                        self.queue.task_done()
                    print "%i items remain" % queue.qsize()


        filters = dict(http_status__in=(None, 200))
        if not options["update_existing"]:
            filters["screenshot"] = None

        total_items = sum([model.objects.filter(**filters).count() for model in models])

        # spawn a pool of threads, and pass them queue instance
        for i in xrange(options["workers_number"]):
            t = process(queue, total_items)
            t.setDaemon(True)
            t.start()

        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            for object_id in model.objects.filter(**filters).values_list("id", flat=True):
                queue.put((content_type.id, object_id))

        queue.join()

        print "Done!"

