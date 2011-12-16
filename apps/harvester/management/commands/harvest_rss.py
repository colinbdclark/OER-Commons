from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, **options):
        from harvester.models import RSSFeed

        for feed in RSSFeed.objects.all():
            feed.harvest()
