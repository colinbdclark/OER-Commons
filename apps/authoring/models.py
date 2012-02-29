from annoying.functions import get_object_or_None
from common.models import GradeLevel
from core.fields import AutoCreateForeignKey, AutoCreateManyToManyField
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from materials.models import  Keyword, \
    GeneralSubject, License
import embedly
import os


class LearningGoal(models.Model):

    title = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title


class AbstractAuthoredMaterial(models.Model):

    title = models.CharField(max_length=200, default=u"")
    text = models.TextField(default=u"")

    summary = models.TextField(default=u"")

    learning_goals = AutoCreateManyToManyField(LearningGoal)
    keywords = AutoCreateManyToManyField(Keyword)
    subjects = models.ManyToManyField(GeneralSubject)
    grade_level = models.ForeignKey(GradeLevel, null=True)
    license = AutoCreateForeignKey(License, null=True, respect_all_fields=True)

    class Meta:
        abstract = True


class AuthoredMaterialDraft(AbstractAuthoredMaterial):

    material = models.OneToOneField("authoring.AuthoredMaterial", related_name="draft")


class AuthoredMaterial(AbstractAuthoredMaterial):

    owners = models.ManyToManyField(User, related_name="+")
    author = models.ForeignKey(User, related_name="+")

    is_new = models.BooleanField(default=True)
    published = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    modified_timestamp = models.DateTimeField(auto_now=True)

    def get_draft(self):
        draft = get_object_or_None(AuthoredMaterialDraft, material=self)
        if not draft:
            draft = AuthoredMaterialDraft(material=self)
            for field in AbstractAuthoredMaterial._meta.fields:
                setattr(draft, field.name, getattr(self, field.name))
            draft.save()
            for m2m in AbstractAuthoredMaterial._meta.many_to_many:
                setattr(draft, m2m.name, getattr(self, m2m.name).all())
        return draft

    @classmethod
    def publish_draft(cls, draft):
        material = draft.material
        for field in AbstractAuthoredMaterial._meta.fields:
            setattr(material, field.name, getattr(draft, field.name))
        for m2m in AbstractAuthoredMaterial._meta.many_to_many:
            setattr(material, m2m.name, getattr(draft, m2m.name).all())
        material.published = True
        material.is_new = False
        material.save()
        draft.delete()
        return material

    @models.permalink
    def get_absolute_url(self):
        return "authoring:view", [], dict(pk=self.pk)


def upload_to(prefix):
    def func(instance, filename):
        return os.path.join("authoring", str(instance.material.id), prefix, filename)
    return func


class Image(models.Model):

    material = models.ForeignKey(AuthoredMaterial)

    image = models.ImageField(upload_to=upload_to("images"))


class Document(models.Model):

    material = models.ForeignKey(AuthoredMaterial)

    file = models.ImageField(upload_to=upload_to("documents"))


class Embed(models.Model):

    url = models.URLField(unique=True, db_index=True, max_length=200)
    type = models.CharField(db_index=True, max_length=20)
    title = models.CharField(max_length=500, null=True, blank=True)
    embed_url = models.URLField(db_index=True, max_length=200, null=True, blank=True) # This is used for photo embeds
    thumbnail = models.URLField(db_index=True, max_length=200, null=True, blank=True)
    html = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.url

    @classmethod
    def get_for_url(cls, url):
        if cls.objects.filter(url=url).exists():
            return cls.objects.get(url=url)

        client = embedly.Embedly(settings.EMBEDLY_KEY)
        if client.is_supported(url):
            result = client.oembed(url, maxwidth="500")
            url = result.url or result.original_url

            if cls.objects.filter(url=url).exists():
                return cls.objects.get(url=url)

            return cls.objects.create(
                url=url,
                type=result.type,
                title=result.title,
                embed_url=url,
                thumbnail=result.thumbnail_url,
                html=result.html,
            )

        return None
