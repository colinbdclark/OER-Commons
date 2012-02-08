from __future__ import absolute_import

from autoslug.fields import AutoSlugField
from cache_utils.decorators import cached
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from materials.models.common import  Keyword
from materials.tasks import reindex_microsite_topic
from mptt.models import MPTTModel
from utils.fields import AutoCreateManyToManyField


class MicrositeManager(models.Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Microsite(models.Model):

    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(max_length=100, populate_from="name")
    keywords = AutoCreateManyToManyField(Keyword)

    objects = MicrositeManager()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"

    def natural_key(self):
        return (self.name,)

    @permalink
    def get_absolute_url(self):
        return ("materials:microsite", [], {"microsite": self.slug})


class TopicManager(models.Manager):

    def get_by_natural_key(self, microsite, name):
        microsite = Microsite.objects.get_by_natural_key(microsite)
        return self.get(microsite=microsite, name=name)


class Topic(MPTTModel):

    name = models.CharField(max_length=100)
    slug = AutoSlugField(max_length=100, populate_from="name")
    keywords = AutoCreateManyToManyField(Keyword, null=True, blank=True)
    microsite = models.ForeignKey(Microsite, related_name="topics")
    parent = models.ForeignKey("self", null=True, blank=True)

    other = models.BooleanField(default=False)

    objects = TopicManager()

    def save(self, *args, **kwargs):
        if self.parent:
            self.microsite = self.parent.microsite
        super(Topic, self).save(*args, **kwargs)
        if self.other:
            self.parent = None
            self.keywords.clear()
        elif not self.keywords.filter(name=self.name).count():
            self.keywords.add(Keyword.objects.get_or_create(name=self.name)[0])

    def clean(self):
        if self.other:
            qs = Topic.objects.filter(microsite=self.microsite, other=True)
            if self.id:
                qs = qs.exclude(pk=self.id)
            if qs.count():
                raise ValidationError(u"Only one 'Other' topic is allowed.")

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.microsite.name, self.name)

    class Meta:
        app_label = "materials"
        ordering = ["microsite", "tree_id", "lft"]
        unique_together = (("name", "microsite"))


def topic_post_save_reindex(sender, **kwargs):
    reindex_microsite_topic.delay(kwargs["instance"])
post_save.connect(topic_post_save_reindex, sender=Topic, dispatch_uid="topic_post_save_reindex")


@cached(60 * 60 * 24)
def get_topic_microsite_from_id(id):
    """
    Lookup a Topic instance by id and return its microsite slug.
    Use caching to reduce the number of database queries. Return None if
    an Topic with given id does not exist.
    """
    try:
        return Topic.objects.get(pk=id).microsite.slug
    except Topic.DoesNotExist:
        return None


