from autoslug.fields import AutoSlugField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from materials.models.common import Author, Keyword, GeneralSubject, GradeLevel, \
    Language, GeographicRelevance, AutoCreateManyToManyField
from materials.models.material import Material


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


class CommunityItem(Material):

    namespace = "community"

    abstract = models.TextField(default=u"", verbose_name=u"Abstract")
    content_creation_date = models.DateField(null=True, blank=True,
                                     verbose_name=_(u"Content creation date"))
    authors = AutoCreateManyToManyField(Author, verbose_name=_(u"Authors"))

    url = models.URLField(max_length=300, verbose_name=_(u"URL"))
    keywords = AutoCreateManyToManyField(Keyword, verbose_name=_(u"Keywords"))

    tech_requirements = models.TextField(default=u"", blank=True,
                                 verbose_name=_(u"Techical requirements"))

    general_subjects = models.ManyToManyField(GeneralSubject,
                                          verbose_name=_(u"General subjects"))
    grade_levels = models.ManyToManyField(GradeLevel,
                                          verbose_name=_(u"Grade level"))
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

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Community item")
        verbose_name_plural = _(u"Community items")
        ordering = ("created_on",)

    def keyword_slugs(self):
        keywords = set(self.keywords.values_list("slug", flat=True))
        keywords.update(self.tags.values_list("slug", flat=True))
        return sorted(keywords)

    def keyword_names(self):
        keywords = set(self.keywords.values_list("name", flat=True))
        keywords.update(self.tags.values_list("name", flat=True))
        return sorted(keywords)

    @permalink
    def get_absolute_url(self):
        return ("materials:%s:view_item" % self.namespace, [], {"slug": self.slug})

    def breadcrumbs(self):
        breadcrumbs = []
        breadcrumbs.append({"url": reverse("materials:community"),
                            "title": u"Community"})
        breadcrumbs.append({"url": self.get_absolute_url(),
                            "title": self.title})
        return breadcrumbs
