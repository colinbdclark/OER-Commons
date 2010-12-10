from autoslug.fields import AutoSlugField
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Tag(models.Model):

    user = models.ForeignKey(User, verbose_name=_(u"User"))
    name = models.CharField(max_length=100, verbose_name=_(u"name"),
                            default=u"")
    slug = AutoSlugField(populate_from="name", verbose_name=_(u"Slug"))
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Tag")
        verbose_name_plural = _(u"Tags")
