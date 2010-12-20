from autoslug.fields import AutoSlugField
from cache_utils.decorators import cached
from django.db import models
from django.utils.translation import ugettext_lazy as _
from materials.ccrest import CcRest
from south.modelsinspector import add_introspection_rules
from urllib2 import HTTPError
import re


class AutoCreateForeignKey(models.ForeignKey):

    def save_form_data(self, instance, data):
        if isinstance(data, dict):
            to = self.rel.to
            data = to.objects.get_or_create(**data)[0]
        super(AutoCreateForeignKey, self).save_form_data(instance, data)
add_introspection_rules([], ["^materials\.models\.common\.AutoCreateForeignKey"])


class AutoCreateManyToManyField(models.ManyToManyField):

    def save_form_data(self, instance, data):
        if isinstance(data, list):
            to = self.rel.to
            for i, value in enumerate(data):
                if isinstance(value, dict):
                    data[i] = to.objects.get_or_create(**value)[0]
        super(AutoCreateManyToManyField, self).save_form_data(instance, data)
add_introspection_rules([], ["^materials\.models\.common\.AutoCreateManyToManyField"])


COU_BUCKETS = (
   (u"no-strings-attached", _(u"No Strings Attached")),
   (u"remix-and-share", _(u"Remix and Share")),
   (u"share-only", _(u"Share Only")),
   (u"read-the-fine-print", _(u"Read the Fine Print")),
)


CC_LICENSE_URL_RE = re.compile(r"^http://(www\.)?creativecommons\.org/licenses/(?P<cc_type>nc-sa|by|by-sa|by-nd|by-nc|by-nc-sa|by-nc-nd)/[0-9]\.[0-9]/?", re.I)
PUBLIC_DOMAIN_URL_RE = re.compile(r"^http://creativecommons.org/licenses/publicdomain/?$", re.I)
GNU_FDL_URL_RE = re.compile(r"^http://www.gnu.org/licenses/fdl.txt$", re.I)

PUBLIC_DOMAIN_URL = u"http://creativecommons.org/licenses/publicdomain/"
PUBLIC_DOMAIN_NAME = u"Public Domain"

GNU_FDL_URL = u"http://www.gnu.org/licenses/fdl.txt"
GNU_FDL_NAME = u"GNU Free Documentation License"


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


class LicenseManager(models.Manager):

    API_ROOT = "http://api.creativecommons.org/rest/1.5"
    STANDARD_LICENSE = 'standard'

    LICENSE_NAME_RE = re.compile(r"<license-name>(.*)</license-name>")
    LICENSE_URL_RE = re.compile(r"<license-uri>(.*)</license-uri>")
    LICENSE_IMG_RE = re.compile(r"<img.*?src=\"(.*?)\".*?>")

    def get_cc_license_name_from_url(self, url):
        url = url.lower()
        if not re.match(CC_LICENSE_URL_RE, url):
            raise ValueError("Invalid CC license URL: %s" % url)

        l_type = url.split('/')[4]
        l_version = url.split('/')[5]

        if l_type == 'nc-sa':
            name = 'Creative Commons Noncommercial-Share Alike'
        elif l_type == 'by':
            name = 'Creative Commons Attribution'
        elif l_type == 'by-sa':
            name = 'Creative Commons Attribution-Share Alike'
        elif l_type == 'by-nd':
            name = 'Creative Commons Attribution-No Derivative Works'
        elif l_type == 'by-nc':
            name = 'Creative Commons Attribution-Noncommercial'
        elif l_type == 'by-nc-sa':
            name = 'Creative Commons Attribution-Noncommercial-Share Alike'
        elif l_type == 'by-nc-nd':
            name = 'Creative Commons Attribution-Noncommercial-No Derivative Works'
        else:
            raise ValueError("Unknown license type: %s" % l_type)
        return name + ' ' + l_version

    @cached(3600)
    def get_cc_issue_fields(self):
        fields = []
        try:
            client = CcRest(self.API_ROOT)
        except HTTPError:
            return fields

        # convert in list
        raw_fields = client.fields(self.STANDARD_LICENSE)
        for k in raw_fields['__keys__']:
            f = raw_fields[k]
            f['id'] = k
            enum = [{'value':value, 'text':text} for value, text in f['enum'].items()]
            if k == 'jurisdiction':
                for i, e in enumerate(enum):
                    if e['value'] == '':
                        generic = enum.pop(i)
                enum.sort(key=lambda x: x['text'])
                enum.insert(0, generic)
            f['enum'] = enum
            fields.append(f)

        return fields

    @cached(3600)
    def issue(self, answers):
        result = {}
        try:
            client = CcRest(self.API_ROOT)
            response = str(client.issue(self.STANDARD_LICENSE, answers))
            result['name'] = self.LICENSE_NAME_RE.findall(response)[0]
            result['url'] = self.LICENSE_URL_RE.findall(response)[0]
            result['img'] = self.LICENSE_IMG_RE.findall(response)[0]
        except:
            return result
        return result


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

    objects = LicenseManager()

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
            return u"cc-" + CC_LICENSE_URL_RE.search(self.url).groupdict()["cc_type"]
        if PUBLIC_DOMAIN_URL_RE.match(self.url):
            return u"public-domain"
        if GNU_FDL_URL_RE.match(self.url):
            return u"gnu-fdl"
        return u"custom"

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

