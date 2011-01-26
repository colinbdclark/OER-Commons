from django.core.management.base import LabelCommand, CommandError
from reports.models import REPORT_TYPES, CHECK_URLS
from optparse import make_option


class Command(LabelCommand):

    help = u"Generates the specified report."
    option_list = LabelCommand.option_list + (
            make_option('--limit',
                action='store',
                type='int',
                dest='limit',
                default=10,
                help='A number of parallel processes used to generate a report. Default: 10'),
            make_option('--timeout',
                action='store',
                type='int',
                dest='timeout',
                default=30,
                help='A timeout value for processing URLs. Default: 30'),
            )

    @property
    def report_types(self):
        return [r[0] for r in REPORT_TYPES]

    @property
    def args(self):
        return "|".join(self.report_types)

    def handle_label(self, label, **options):
        if label not in self.report_types:
            raise CommandError(u"Invalid report type: %s" % label)

        if label == CHECK_URLS:
            from reports.check_urls import process_check_urls
            process_check_urls(limit=options["limit"],
                               timeout=options["timeout"])

