from autoslug.fields import AutoSlugField
from django.db import models
from django.db.models.signals import pre_delete, m2m_changed, post_save
from django.utils.translation import ugettext_lazy as _
from materials.models.common import Author, Keyword, GeneralSubject, GradeLevel, \
    Language, GeographicRelevance, MediaFormat, Institution, Collection, \
    AutoCreateManyToManyField, AutoCreateForeignKey
from materials.models.material import Material, mark_for_reindex, \
    unindex_material


class LibraryMaterialType(models.Model):

    name = models.CharField(unique=True, max_length=100,
                            verbose_name=_(u"Name"))
    slug = AutoSlugField(unique=True, max_length=100, populate_from="name",
                         verbose_name=_(u"Slug"),
                         db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Library material type")
        verbose_name_plural = _(u"Library material types")
        ordering = ("id",)


class Library(Material):

    namespace = "libraries"

    provider_id = models.CharField(max_length=300, default=u"", blank=True,
                                   verbose_name=_(u"Provider ID"))

    abstract = models.TextField(default=u"", verbose_name=u"Abstract")
    content_creation_date = models.DateField(null=True, blank=True,
                                     verbose_name=_(u"Content creation date"))
    authors = AutoCreateManyToManyField(Author, verbose_name=_(u"Authors"),
                                        respect_all_fields=True)

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
    material_types = models.ManyToManyField(LibraryMaterialType,
                                            verbose_name=_(u"Material types"))
    media_formats = models.ManyToManyField(MediaFormat,
                                           verbose_name=_(u"Media formats"))

    institution = AutoCreateForeignKey(Institution, null=True, blank=True,
                                    verbose_name=_(u"Institution"))
    collection = AutoCreateForeignKey(Collection, null=True, blank=True,
                                   verbose_name=_(u"Collection"))

    curriculum_standards = models.TextField(default=u"", blank=True,
                                        verbose_name=_("Curriculum standards"))

    is_homepage = models.BooleanField(default=False,
                                      verbose_name=_(u"Homepage"))

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "materials"
        verbose_name = _(u"Library and Collection")
        verbose_name_plural = _(u"Libraries and Collections")
        ordering = ("created_on",)


post_save.connect(mark_for_reindex, sender=Library, dispatch_uid="library_post_save_reindex")
m2m_changed.connect(mark_for_reindex, sender=Library, dispatch_uid="library_m2m_changed_reindex")
pre_delete.connect(unindex_material, sender=Library, dispatch_uid="library_pre_delete_unindex")
