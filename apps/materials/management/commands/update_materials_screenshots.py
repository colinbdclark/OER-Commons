from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = u"Update materials screenshots."

    def handle(self, **options):
        from materials.models import CommunityItem
        from materials.models.course import Course
        from materials.models.library import Library
        from materials.tasks import update_screenshot

        models = [Course, Library, CommunityItem]

        filters = dict(http_status=200, screenshot=None)

        print "Updating screenshots..."

        for model in models:
            for item in model.objects.filter(**filters):
                update_screenshot(item)

        print "Done!"

