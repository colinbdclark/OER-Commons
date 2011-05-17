from django.core.management.base import BaseCommand
from stats.report import send_report
import datetime


class Command(BaseCommand):

    help = u"Send a report with weekly statistics."
    option_list = BaseCommand.option_list

    def handle(self, **options):
        send_report(interval=datetime.timedelta(days=7))
