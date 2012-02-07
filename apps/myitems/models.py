import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug.fields import AutoSlugField


class Folder(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField()
    slug = AutoSlugField(populate_from="name", verbose_name=_(u"Slug"))
    timestamp = models.DateTimeField(auto_now_add=True)



class FolderItem(models.Model):
    folder = models.ForeignKey(Folder)
    content_type = models.ForeignKey(ContentType,
        verbose_name=_(u"Content type"),
        db_index=True)
    object_id = models.PositiveIntegerField(verbose_name=_(u"Object ID"),
        db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
