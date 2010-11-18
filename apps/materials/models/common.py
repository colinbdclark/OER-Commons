from autoslug.fields import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _


COU_BUCKETS = (
   (u"no-strings-attached", _(u"No Strings Attached")),
   (u"remix-and-share", _(u"Remix and Share")),
   (u"share-only", _(u"Share Only")),
   (u"read-the-fine-print", _(u"Read the Fine Print")),
)


class License(models.Model):

    url = models.URLField(max_length=300, default=u"", blank=True,
                          verbose_name=_(u"License URL"))
    name = models.CharField(max_length=300, default=u"",
                            verbose_name=_(u"License name"))
    image_url = models.URLField(max_length=300, default=u"", blank=True,
                                verbose_name=_(u"License image URL"))
    description = models.TextField(default=u"", blank=True,
                                  verbose_name=_(u"License description"))
    copyright_holder = models.CharField(max_length=2000, default=u"",
                                        blank=True,
                                        verbose_name=_(u"Copyright holder"))
    bucket = models.CharField(max_length=50, choices=COU_BUCKETS, default=u"",
                              blank=True, verbose_name=_(u"Bucket"))

    def __unicode__(self):
        return self.name or self.url

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")
        ordering = ("id",)


class Country(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")
        ordering = ("id",)


class Author(models.Model):

    name = models.CharField(max_length=200, verbose_name=_(u"Name"))
    email = models.EmailField(max_length=200, blank=True, default=u"",
                              verbose_name=_(u"Email"))
    country = models.ForeignKey(Country, null=True, blank=True,
                                verbose_name=_(u"Country"))

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Author")
        verbose_name_plural = _(u"Authors")
        ordering = ("name",)


class Keyword(models.Model):

    name = models.CharField(unique=True, max_length=500,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)
    suggested = models.BooleanField(default=False,
                                    verbose_name=_(u"Suggested"))

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Keyword")
        verbose_name_plural = _(u"Keywords")
        ordering = ("name",)


class GeneralSubject(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)
    description = models.TextField(default=u"", blank=True,
                                   verbose_name=_(u"Description"))

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"General subject")
        verbose_name_plural = _(u"General subjects")
        ordering = ("id",)


class GradeLevel(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)
    description = models.TextField(default=u"", blank=True,
                                   verbose_name=_(u"Description"))

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Grade level")
        verbose_name_plural = _(u"Grade levels")
        ordering = ("id",)


class Language(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = models.SlugField(max_length=3, unique=True,
                            verbose_name=_(u"Slug"),
                            db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Language")
        verbose_name_plural = _(u"Languages")
        ordering = ("name",)


class Collection(models.Model):

    name = models.CharField(unique=True, max_length=300,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Collection")
        verbose_name_plural = _(u"Collections")
        ordering = ("name",)


class Institution(models.Model):

    name = models.CharField(unique=True, max_length=300,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Institution")
        verbose_name_plural = _(u"Institutions")
        ordering = ("name",)


class MediaFormat(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Media format")
        verbose_name_plural = _(u"Media formats")
        ordering = ("id",)


class GeographicRelevance(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Geographic relevance")
        verbose_name_plural = _(u"Geographic relevances")
        ordering = ("id",)

