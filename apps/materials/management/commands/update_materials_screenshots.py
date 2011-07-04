from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from materials.models import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from materials.tasks import update_screenshot, check_url_status
import traceback


class Command(BaseCommand):

    help = u"Update materials screenshots."
    option_list = BaseCommand.option_list + (
            make_option('--update-existing',
                action='store_true',
                dest='update_existing',
                default=False,
                help='Update existing screenshots.'),
            )

    def handle(self, **options):

        models = [Course, Library, CommunityItem]

        filters = dict(http_status__in=(None, 200))
        if not options["update_existing"]:
            filters["screenshot"] = None

        total_items = sum([model.objects.filter(**filters).count() for model in models])

        print "Updating screenshots for %i items..." % total_items
        cnt = 0
        for model in models:
            for object_id in model.objects.filter(**filters).values_list("id", flat=True):
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
                        print "Exception while processing %s %i" % (model._meta.object_name, object_id)
                        print traceback.format_exc()
                cnt += 1
                print "%i of %i..." % (cnt, total_items)

        print "Done!"

