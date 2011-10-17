from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_extensions.utils.text import truncate_letters


class StandardManager(models.Manager):

    def get_by_natural_key(self, code, substandard_code):
        return self.get(code=code, substandard_code=substandard_code)


class Standard(models.Model):

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=4, db_index=True)

    substandard_code = models.CharField(max_length=20, db_index=True, default=u"")

    objects = StandardManager()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)

    def natural_key(self):
        return self.code, self.substandard_code

    class Meta:
        unique_together = ["code", "substandard_code"]
        ordering = ("id", )


class GradeManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class Grade(models.Model):

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, db_index=True)

    objects = GradeManager()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)

    def natural_key(self):
        return self.code,

    class Meta:
        ordering = ("id", )


class LearningObjectiveCategoryManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class LearningObjectiveCategory(models.Model):

    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=8, unique=True, db_index=True)

    objects = LearningObjectiveCategoryManager()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)

    def natural_key(self):
        return self.code,

    class Meta:
        ordering = ("id", )
        verbose_name_plural = u"Learning objective categories"


class AlignmentTagManager(models.Manager):

    def get_from_full_code(self, code):
        parts = code.split(".")[1:]
        assert 3 <= len(parts) <= 4
        if len(parts) == 3:
            return self.get_by_natural_key(*parts)
        else:
            try:
                return self.get_by_natural_key(*[parts[0], ".".join(parts[1:3]), parts[3]])
            except AlignmentTag.DoesNotExist:
                return self.get_by_natural_key(*[parts[0], parts[1], ".".join(parts[2:])])

    def get_by_natural_key(self, grade_code, category_code, code):
        return self.get(grade__code=grade_code, category__code=category_code,
                        code=code)


class AlignmentTag(models.Model):

    description = models.TextField()
    standard = models.ForeignKey(Standard)
    grade = models.ForeignKey(Grade)
    category = models.ForeignKey(LearningObjectiveCategory)
    subcategory = models.TextField(verbose_name=u"Domain")
    code = models.CharField(max_length=10, db_index=True)

    objects = AlignmentTagManager()

    @property
    def full_code(self):
        return "%s.%s.%s.%s" % (self.standard.code, self.grade.code,
                                self.category.code, self.code)

    def natural_key(self):
        return (self.grade.code, self.category.code, self.code,)

    def __unicode__(self):
        return "%s - %s" % (self.full_code, truncate_letters(self.description,
                                                             70))

    class Meta:
        ordering = ("standard", "grade", "category", "code",)
        unique_together = ("grade", "category", "code")


class TaggedMaterial(models.Model):

    tag = models.ForeignKey(AlignmentTag, db_index=True)
    user = models.ForeignKey(User, db_index=True)

    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)

    content_object = GenericForeignKey()

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return "%s - %s by %s" % (unicode(self.content_object),
                                  self.tag.full_code,
                                  unicode(self.user))

    class Meta:
        unique_together = ("user", "tag", "content_type", "object_id")
