from autoslug import AutoSlugField
from common.fields import SeparatedValuesField
from common.models import StudentLevel, GeneralSubject, Language, Keyword
from django.contrib.auth.models import User
from django.db import models
from materials.models import AutoCreateManyToManyField
from sorl.thumbnail import get_thumbnail


class Group(models.Model):

    user = models.ForeignKey(User)

    title = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title


class OER(models.Model):

    author = models.ForeignKey(User, null=True)
    is_new = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    title = models.CharField(max_length=200, default=u"")
    slug = AutoSlugField(populate_from="title")

    student_levels = models.ManyToManyField(StudentLevel)
    subjects = models.ManyToManyField(GeneralSubject)

    summary = models.TextField(default=u"")

    goals = SeparatedValuesField(default=u"")

    language = models.ForeignKey(Language, null=True, blank=True)

    image = models.ImageField(null=True, blank=True,
                              upload_to="upload/oer/oer")

    group = models.ForeignKey(Group, null=True, blank=True)

    instruction_date = models.DateTimeField(null=True, blank=True)

    keywords = AutoCreateManyToManyField(Keyword)

    def __unicode__(self):
        return self.title or self.id

    def save(self, *args, **kwargs):
        if not self.title and not self.summary:
            self.is_new = True
        else:
            self.is_new = False
        super(OER, self).save(*args, **kwargs)

    def get_thumbnail(self):
        if not self.image:
            return None
        return get_thumbnail(self.image, "220x500")


class Chapter(models.Model):

    oer = models.ForeignKey(OER, related_name="chapters")
    order = models.PositiveIntegerField()
    title = models.CharField(default=u"", max_length=200)
    text = models.TextField(default=u"")

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return u"%s from %s" % (self.title, unicode(self.oer))

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = self.oer.chapters.all().count() + 1
        super(Chapter, self).save(*args, **kwargs)

    class Meta:
        ordering = ["oer__id", "order", "id"]

