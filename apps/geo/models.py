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

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "geo"
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")
        ordering = ("name",)


