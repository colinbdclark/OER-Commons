from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_extensions.utils.text import truncate_letters


class StandardManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class Standard(models.Model):

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=4, unique=True, db_index=True)

    objects = StandardManager()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)

    def natural_key(self):
        return (self.code,)

    class Meta:
        ordering = ("code",)


class GradeManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class Grade(models.Model):

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=4, unique=True, db_index=True)

    objects = GradeManager()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)

    def natural_key(self):
        return (self.code,)

    class Meta:
        ordering = ("id", )


class LearningObjectiveCategoryManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class LearningObjectiveCategory(models.Model):

    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=4, unique=True, db_index=True)

    objects = LearningObjectiveCategoryManager()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)

    def natural_key(self):
        return (self.code,)

    class Meta:
        ordering = ("id", )
        verbose_name_plural = u"Learning objective categories"


class AlignmentTagManager(models.Manager):

    def get_by_natural_key(self, standard_code, grade_code, category_code, code):
        return self.get(standard__code=standard_code, grade__code=grade_code,
                        category__code=category_code, code=code)


class AlignmentTag(models.Model):

    description = models.TextField()
    standard = models.ForeignKey(Standard)
    grade = models.ForeignKey(Grade)
    category = models.ForeignKey(LearningObjectiveCategory)
    subcategory = models.TextField()
    code = models.CharField(max_length=4, db_index=True)

    objects = AlignmentTagManager()

    @property
    def full_code(self):
        return ".".join(self.natural_key())

    def natural_key(self):
        return (self.standard.code, self.grade.code, self.category.code,
                self.code,)

    def __unicode__(self):
        return "%s - %s" % (self.full_code, truncate_letters(self.description,
                                                             70))

    class Meta:
        ordering = ("standard", "grade", "category", "code",)
        unique_together = ("standard", "grade", "category", "code")


class TaggedMaterial(models.Model):

    tag = models.ForeignKey(AlignmentTag, db_index=True)
    user = models.ForeignKey(User, db_index=True)

    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)

    content_object = GenericForeignKey('content_type', 'object_id')

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return "%s - %s by %s" % (unicode(self.content_object),
                                  self.tag.full_code,
                                  unicode(self.user))

    class Meta:
        unique_together = ("user", "tag", "content_type", "object_id")
        