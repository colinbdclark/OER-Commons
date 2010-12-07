from autoslug.fields import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _
import re


COU_BUCKETS = (
   (u"no-strings-attached", _(u"No Strings Attached")),
   (u"remix-and-share", _(u"Remix and Share")),
   (u"share-only", _(u"Share Only")),
   (u"read-the-fine-print", _(u"Read the Fine Print")),
)


CC_LICENSE_URL_RE = re.compile(r"^http://(www\.)?creativecommons\.org/licenses/(?P<cc_type>nc-sa|by|by-sa|by-nd|by-nc|by-nc-sa|by-nc-nd)/[0-9]\.[0-9]/?$", re.I)
PUBLIC_DOMAIN_URL_RE = re.compile(r"^http://creativecommons.org/licenses/publicdomain/?$", re.I)
GNU_FDL_URL_RE = re.compile(r"^http://www.gnu.org/licenses/fdl.txt$", re.I)


LICENSE_TYPES = (
    (u"cc-nc-sa", u"CC Noncommercial-Share Alike"),
    (u"cc-by", u"CC Attribution"),
    (u"cc-by-sa", u"CC Attribution-Share Alike"),
    (u"cc-by-nd", u"CC Attribution-No Derivative Works"),
    (u"cc-by-nc", u"CC Attribution-Noncommercial"),
    (u"cc-by-nc-sa", u"CC Attribution-Noncommercial-Share Alike"),
    (u"cc-by-nc-nd", u"CC Attribution-Noncommercial-No Derivative Works"),
    (u"public-domain", u"Public Domain"),
    (u"gnu-fdl", u"GNU FDL"),
    (u"custom", u"Custom"),
)


LICENSE_HIERARCHY = (
    (u"no-strings-attached", ("cc-by", "public-domain")),
    (u"remix-and-share", ("cc-by-sa", "cc-by-nc", "cc-by-nc-sa", "cc-nc-sa", "gnu-fdl")),
    (u"share-only", ("cc-by-nd", "cc-by-nc-nd")),
    (u"read-the-fine-print", ()),
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

    @property
    def type(self):
        if CC_LICENSE_URL_RE.match(self.url):
            return "cc-" + CC_LICENSE_URL_RE.groupdict(self.url)["cc_type"]
        if PUBLIC_DOMAIN_URL_RE.match(self.url):
            return "public-domain"
        if GNU_FDL_URL_RE.match(self.url):
            return "gnu-fdl"
        return "custom"

    @property
    def image(self):
        # TODO: fix this
        return self.image_url


class Country(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100,
                         populate_from="name",
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
    slug = AutoSlugField(populate_from="name", max_length=500,
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
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
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
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
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
    slug = AutoSlugField(unique=True, max_length=300, populate_from="name",
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
    slug = AutoSlugField(unique=True, max_length=300, populate_from="name",
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
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
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
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Geographic relevance")
        verbose_name_plural = _(u"Geographic relevances")
        ordering = ("id",)

