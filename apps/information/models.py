from django.db import models
from autoslug.fields import AutoSlugField


class Topic(models.Model):

    title = models.CharField(max_length=500)
    short_title = models.CharField(max_length=500, null=True, blank=True)
    slug = AutoSlugField(max_length=500, populate_from='title', unique=True)
    text = models.TextField()
    order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ["order"]


class HelpTopic(Topic):
    pass


class AboutTopic(Topic):
    pass
