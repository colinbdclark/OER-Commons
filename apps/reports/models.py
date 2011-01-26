from django.conf import settings
from django.db import models
from django.utils.dateformat import format


CHECK_URLS = u"check_urls"


REPORT_TYPES = (
    (CHECK_URLS, "Check URLs"),
)


class Report(models.Model):

    type = models.CharField(max_length=30,
                            choices=REPORT_TYPES)

    timestamp = models.DateTimeField(auto_now_add=True)

    file = models.FileField(upload_to="reports")

    def __unicode__(self):
        return "%s : %s" % (self.get_type_display(),
                            format(self.timestamp, settings.DATETIME_FORMAT))

    class Meta:
        ordering = ["-timestamp"]

