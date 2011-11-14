from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime


RATING_VALUES = (
    (5, u"5 (best)"),
    (4, u"4"),
    (3, u"3"),
    (2, u"2"),
    (1, u"1"),
)


class Rating(models.Model):

    user = models.ForeignKey(User)

    value = models.SmallIntegerField(choices=RATING_VALUES)

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"))
    content_object = generic.GenericForeignKey()

    timestamp = models.DateTimeField(auto_now_add=True,
                                     default=datetime.datetime.now)

    def __unicode__(self):
        return u"'%s' rated by %s - %i" % (self.content_object, self.user,
                                           self.value)

    class Meta:
        verbose_name = _(u"Rating")
        verbose_name_plural = _(u"Ratings")
        unique_together = ["content_type", "object_id", "user"]
