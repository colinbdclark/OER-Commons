from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.db import models
from django.template.loader import render_to_string
import re
from django.conf import settings


FEEDBACK_TYPES = (
    (u"bug", u"Bug"),
    (u"feature-request", u"Feature request"),
    (u"general-comment", u"General comment"),
)


class FeedbackMessage(models.Model):

    URL_RE = re.compile("https?://")

    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    subject = models.TextField()
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    spam = models.BooleanField(default=False)

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ["-timestamp"]

    def send(self):
        site_url = "http://%s" % Site.objects.get_current().domain
        body = render_to_string("feedback/emails/message.html",
                                dict(message=self, site_url=site_url))
        subject = u"OER Commons Feedback: [%s] - %s" % (self.get_type_display(), self.subject)
        message = EmailMessage(subject, body, self.email, to=[settings.DEFAULT_FROM_EMAIL])
        message.content_subtype = "html"
        message.send()

    def save(self, *args, **kwargs):
        # Mark message as spam if it contains more than 2 urls in text
        if len(self.URL_RE.findall(self.text)) > 2:
            self.spam = True

        # If this message was just added and it's not spam then send it to
        # site's admin
        if not self.id and not self.spam:
            self.send()
        super(FeedbackMessage, self).save(*args, **kwargs)
