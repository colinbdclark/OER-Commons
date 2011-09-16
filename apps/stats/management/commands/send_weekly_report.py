from django.core.management.base import BaseCommand
from optparse import make_option
import datetime


class Command(BaseCommand):

    help = u"Send a report with weekly statistics."
    option_list = BaseCommand.option_list + (
        make_option('--to-date',
            action='store',
            type='string',
            dest='to_date',
            default=None,
            help='The upper date of the report interval (ISO format). Default: None'),

    )

    def handle(self, **options):
        from stats.report import send_report
        to_date = options["to_date"]
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
        send_report(interval=datetime.timedelta(days=7), to_date=to_date)
