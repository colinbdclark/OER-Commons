from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):

    help = u"Update materials screenshots."

    def handle(self, **options):
        from materials.models import CommunityItem
        from materials.models.course import Course
        from materials.models.library import Library
        from materials.tasks import update_screenshot

        print "Updating screenshots..."

        for model in (Course, Library, CommunityItem):
            for item in model.objects.filter(http_status=200).filter(
                models.Q(screenshot=None) | models.Q(screenshot=u"")
            ): update_screenshot(item)

        print "Done!"

