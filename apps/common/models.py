from autoslug import AutoSlugField
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _


class StudentLevel(models.Model):

    title = models.CharField(max_length=100)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ("id",)


class GradeLevel(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)
    description = models.TextField(default=u"", blank=True,
                                   verbose_name=_(u"Description"))

    start_age = models.IntegerField(default=0)
    end_age = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Grade level")
        verbose_name_plural = _(u"Grade levels")
        ordering = ("id",)

    @permalink
    def get_absolute_url(self):
        return "materials:grade_level_index", [], {"grade_levels": self.slug}


class GradeSubLevel(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    grade_level = models.ForeignKey(GradeLevel)

    start_age = models.IntegerField(default=0)
    end_age = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Grade sub-level")
        verbose_name_plural = _(u"Grade sub-levels")
        ordering = ("id",)


class GradeManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class Grade(models.Model):

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, db_index=True)
    grade_sublevel = models.ForeignKey(GradeSubLevel, null=True)
    order = models.IntegerField(default=0)

    start_age = models.IntegerField(default=0)
    end_age = models.IntegerField(null=True, blank=True)

    objects = GradeManager()

    def __unicode__(self):
        return "%s" % self.name

    def natural_key(self):
        return self.code,

    class Meta:
        ordering = ("order", "id", )


class MediaFormat(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Media format")
        verbose_name_plural = _(u"Media formats")
        ordering = ("id",)
