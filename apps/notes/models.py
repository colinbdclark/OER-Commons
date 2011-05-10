from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Note(models.Model):
    ''' This model is obsolete. It's not removed only to keep existing data
    in databse. '''

    user = models.ForeignKey(User)

    text = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u"'%s' noted by %s" % (self.content_object, self.user)

    class Meta:
        verbose_name = _(u"Note")
        verbose_name_plural = _(u"Notes")

