from autoslug.fields import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CountryManager(models.Manager):
    
    def get_by_natural_key(self, code):
        return self.get(code=code)


class Country(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100,
                         populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)
    code = models.CharField(unique=True, max_length=2, db_index=True)

    objects = CountryManager()

    def natural_key(self):
        return [self.code, ]
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "geo"
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")
        ordering = ("name",)


class CountryIPDiapasonManager(models.Manager):
    
    def ip2int(self, ip):
        parts = map(lambda x: int(x), ip.split("."))
        parts.reverse()
        sum = 0
        for i, part in enumerate(parts):
            sum += part * (256 ** i)
        return sum    

    def get_country_by_ip(self, ip):
        int_ip = self.ip2int(ip)
        results = self.filter(start__lte=int_ip, end__gte=int_ip)
        if results.exists():
            return results[0].country
        return None


class CountryIPDiapason(models.Model):
    
    country = models.ForeignKey(Country)
    start = models.BigIntegerField(db_index=True)
    end = models.BigIntegerField(db_index=True)
    
    objects = CountryIPDiapasonManager()
    
    class Meta:
        verbose_name = _(u"Country IP Diapason")
        verbose_name_plural = _(u"Country IP Diapasons")
        ordering = ("country",)
        
    def __unicode__(self):
        return u"%s %i - %i" % (self.country.name, self.start, self.end)


class USStateManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class USState(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100,
                         populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)
    code = models.CharField(unique=True, max_length=2, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ("name", )
        verbose_name = u"US State"
        verbose_name_plural = u"US States"

    def natural_key(self):
        return [self.code, ]

