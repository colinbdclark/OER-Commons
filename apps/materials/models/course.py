from __future__ import absolute_import

from autoslug.fields import AutoSlugField
from common.models import GeneralSubject, Language
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save, m2m_changed, pre_delete
from django.utils.translation import ugettext_lazy as _
from materials.models import material_post_save
from materials.models.common import Author, Keyword, GradeLevel,\
    GeographicRelevance, MediaFormat, Institution, Collection, \
    AutoCreateManyToManyField, AutoCreateForeignKey
from materials.models.material import Material, mark_for_reindex, \
    unindex_material


COURSE_OR_MODULE = (
   (u"full-course", _(u"Full Course")),
   (u"learning-module", _(u"Learning Module")),
)

RELATIONSHIP_TYPES = (
   (u"prerequisite", _(u"Prerequisite")),
   (u"postrequisite", _(u"Postrequisite")),
   (u"derived", _(u"Derived")),
)


class CourseMaterialType(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Course material type")
        verbose_name_plural = _(u"Course material types")
        ordering = ("id",)

    @permalink
    def get_absolute_url(self):
        return "materials:courses:material_type_index", [], {"course_material_types": self.slug}


class RelatedMaterial(models.Model):

    title = models.CharField(max_length=200, verbose_name=_(u"Title"))
    url = models.URLField(max_length=300, default=u"", blank=True,
                          verbose_name=_(u"URL"))
    description = models.TextField(default=u"", blank=True,
                                   verbose_name=_(u"Description"))

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Related material")
        verbose_name_plural = _(u"Related materials")
        ordering = ("title",)


class Course(Material):

    namespace = "courses"

    course_id = models.CharField(max_length=300, default=u"", blank=True,
                                 verbose_name=_(u"Course ID"))
    provider_id = models.CharField(max_length=300, default=u"", blank=True,
                                   verbose_name=_(u"Provider ID"))

    abstract = models.TextField(default=u"", verbose_name=u"Abstract")
    content_creation_date = models.DateField(null=True, blank=True,
                                     verbose_name=_(u"Content creation date"))
    authors = AutoCreateManyToManyField(Author, verbose_name=_(u"Authors"),
                                        respect_all_fields=True)

    url = models.URLField(max_length=300, verbose_name=_(u"URL"), verify_exists=False)
    keywords = AutoCreateManyToManyField(Keyword, verbose_name=_(u"Keywords"))

    tech_requirements = models.TextField(default=u"", blank=True,
                                     verbose_name=_(u"Techical requirements"))

    general_subjects = models.ManyToManyField(GeneralSubject,
                                          verbose_name=_(u"General subjects"))
    grade_levels = models.ManyToManyField(GradeLevel,
                                          verbose_name=_(u"Grade level"))
    languages = models.ManyToManyField(Language, verbose_name=_(u"Languages"))
    geographic_relevance = models.ManyToManyField(GeographicRelevance,
                                      verbose_name=_(u"Geographic relevance"))
    material_types = models.ManyToManyField(CourseMaterialType,
                                            verbose_name=_(u"Material types"))
    media_formats = models.ManyToManyField(MediaFormat,
                                           verbose_name=_(u"Media formats"))

    institution = AutoCreateForeignKey(Institution, null=True, blank=True,
                                    verbose_name=_(u"Institution"))
    collection = AutoCreateForeignKey(Collection, null=True, blank=True,
                                   verbose_name=_(u"Collection"))

    curriculum_standards = models.TextField(default=u"", blank=True,
                                    verbose_name=_("Curriculum standards"))
    course_or_module = models.CharField(max_length=50, default=u"", blank=True,
                                        choices=COURSE_OR_MODULE,
                                    verbose_name=_(u"Full course or module"))

    prerequisite_1 = AutoCreateForeignKey(RelatedMaterial, null=True, blank=True,
                                       verbose_name=_(u"Pre-requisite 1"),
                                       related_name="prerequisites_1")

    prerequisite_2 = AutoCreateForeignKey(RelatedMaterial, null=True, blank=True,
                                       verbose_name=_(u"Pre-requisite 2"),
                                       related_name="prerequisites_2")

    postrequisite_1 = AutoCreateForeignKey(RelatedMaterial, null=True, blank=True,
                                       verbose_name=_(u"Post-requisite 1"),
                                       related_name="postrequisites_1")

    postrequisite_2 = AutoCreateForeignKey(RelatedMaterial, null=True, blank=True,
                                       verbose_name=_(u"Post-requisite 2"),
                                       related_name="postrequisites_2")

    derived_from = AutoCreateForeignKey(RelatedMaterial, null=True, blank=True,
                                       verbose_name=_(u"Derived From"),
                                       related_name="derived")

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Course Related Material")
        verbose_name_plural = _(u"Course Related Materials")
        ordering = ("created_on",)


post_save.connect(mark_for_reindex, sender=Course, dispatch_uid="course_post_save_reindex")
post_save.connect(material_post_save, sender=Course, dispatch_uid="course_post_save")
m2m_changed.connect(mark_for_reindex, sender=Course, dispatch_uid="course_m2m_changed_reindex")
pre_delete.connect(unindex_material, sender=Course, dispatch_uid="course_pre_delete_unindex")

