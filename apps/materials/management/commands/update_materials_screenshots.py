from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):

    help = u"Update materials screenshots."

    def handle(self, **options):
        from materials.models.material import PUBLISHED_STATE
        from materials.models import CommunityItem
        from materials.models.course import Course
        from materials.models.library import Library
        from authoring.models import AuthoredMaterial

        from materials.tasks import update_screenshot

        for model in (Course, Library, CommunityItem):
            for item in model.objects.filter(http_status=200).filter(
                models.Q(screenshot=None) | models.Q(screenshot=u"")
            ): update_screenshot(item)

        for item in AuthoredMaterial.objects.filter(workflow_state=PUBLISHED_STATE).filter(
            models.Q(screenshot=None) | models.Q(screenshot=u"")
        ): update_screenshot(item)
