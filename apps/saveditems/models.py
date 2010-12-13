from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SavedItem(models.Model):

    user = models.ForeignKey(User)

    timestamp = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u"'%s' saved by %s" % (self.content_object, self.user)

    class Meta:
        verbose_name = _(u"Saved Item")
        verbose_name_plural = _(u"Saved Items")

