from __future__ import absolute_import

from autoslug.fields import AutoSlugField
from common.models import GradeLevel, GradeSubLevel, Grade
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from materials.models.common import Author, Keyword, GeneralSubject,\
    Language, GeographicRelevance
from materials.models.material import Material
from utils.fields import AutoCreateManyToManyField


class CommunityType(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Community type")
        verbose_name_plural = _(u"Community types")
        ordering = ("id",)

    @permalink
    def get_absolute_url(self):
        return "materials:community:community_type_index", [], {"community_types": self.slug}


class CommunityTopic(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Community topic")
        verbose_name_plural = _(u"Community topics")
        ordering = ("id",)

    @permalink
    def get_absolute_url(self):
        return "materials:community:community_topic_index", [], {"community_topics": self.slug}


class CommunityItem(Material):

    namespace = "community"

    abstract = models.TextField(default=u"", verbose_name=u"Abstract")
    content_creation_date = models.DateField(null=True, blank=True,
                                     verbose_name=_(u"Content creation date"))
    authors = AutoCreateManyToManyField(Author, verbose_name=_(u"Authors"),
                                        respect_all_fields=True)

    keywords = AutoCreateManyToManyField(Keyword, verbose_name=_(u"Keywords"))

    tech_requirements = models.TextField(default=u"", blank=True,
                                 verbose_name=_(u"Techical requirements"))

    general_subjects = models.ManyToManyField(GeneralSubject,
                                          verbose_name=_(u"General subjects"))
    grade_levels = models.ManyToManyField(GradeLevel,
                                          verbose_name=_(u"Grade level"))
    grade_sublevels = models.ManyToManyField(GradeSubLevel,
                                          verbose_name=_(u"Grade sub-level"))
    grades = models.ManyToManyField(Grade, verbose_name=_(u"Grade"))
    languages = models.ManyToManyField(Language,
                                       verbose_name=_(u"Languages"))
    geographic_relevance = models.ManyToManyField(GeographicRelevance,
                                      verbose_name=_(u"Geographic relevance"))
    community_types = models.ManyToManyField(CommunityType,
                                         verbose_name=_(u"Community types"))
    community_topics = models.ManyToManyField(CommunityTopic,
                                          verbose_name=_(u"Community topics"))

    community_featured = models.BooleanField(default=False,
                             verbose_name=_(u"Featured on the Community Page"))
    news_featured = models.BooleanField(default=False,
                        verbose_name=_(u"Featured Open Content Buzz Portlet"))

    # New fields
    new_subject = models.TextField(default="", blank=True)
    new_level = models.TextField(default="", blank=True)
    audience = models.TextField(default="", blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Community item")
        verbose_name_plural = _(u"Community items")
        ordering = ("created_on",)

    @classmethod
    @permalink
    def get_parent_url(cls):
        return "materials:community", [], {}
