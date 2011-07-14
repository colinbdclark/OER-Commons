from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _


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
        verbose_name = _(u"General subject")
        verbose_name_plural = _(u"General subjects")
        ordering = ("id",)

    @models.permalink
    def get_absolute_url(self):
        return "materials:general_subject_index", [], {"general_subjects": self.slug}


class StudentLevel(models.Model):

    title = models.CharField(max_length=100)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ("id",)
        