import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = u"Fetch OER materials URLs and update screenshots."

    def handle(self, **options):

        from materials.models import CommunityItem
        from materials.models.course import Course
        from materials.models.library import Library
        from materials.tasks import check_url_status, update_screenshot
        from utils import update_item

        models = [Course, Library, CommunityItem]

        now = datetime.datetime.now()

        items = []

        # Get items that were never fetched
        for model in models:
            qs = model.objects.filter(url_fetched_on=None)
            if qs.exists():
                items += list(qs)
                qs.update(url_fetched_on=now)

        if not items:
            # Get the item with the oldest fetch date
            item = None
            for model in models:
                qs =  model.objects.exclude(url_fetched_on=None).order_by("url_fetched_on")
                if not qs.exists():
                    continue
                candidate = qs[0]
                if item is None or candidate.url_fetched_on < item.url_fetched_on:
                    item = candidate

            if item is not None:
                update_item(item, url_fetched_on=now)
                items.append(item)

        if not items:
            print "No items to fetch."
            return

        for item in items:
            print "Fetching URL for ", unicode(item)
            check_url_status(item)
            update_screenshot(item)

        print "Done!"

