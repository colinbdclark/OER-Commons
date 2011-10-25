from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from haystack_scheduled.indexes import Indexed


class Review(models.Model):

    user = models.ForeignKey(User)

    text = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"))
    content_object = generic.GenericForeignKey()

    def __unicode__(self):
        return u"'%s' reviewed by %s" % (self.content_object, self.user)

    class Meta:
        verbose_name = _(u"Review")
        verbose_name_plural = _(u"Reviews")


#noinspection PyUnusedLocal
@receiver(models.signals.post_save, sender=Review)
def review_post_save(sender, **kwargs):
    instance = kwargs["instance"]
    content_object = instance.content_object
    if isinstance(content_object, Indexed):
        content_object.reindex()


#noinspection PyUnusedLocal
@receiver(models.signals.post_delete, sender=Review)
def review_post_delete(sender, **kwargs):
    instance = kwargs["instance"]
    content_object = instance.content_object
    if isinstance(content_object, Indexed):
        content_object.reindex()
