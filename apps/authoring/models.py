from common.models import GradeLevel
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from materials.models import  Keyword, \
    GeneralSubject, Language
from utils.fields import AutoCreateManyToManyField
import embedly
import os


class LearningGoal(models.Model):

    title = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title


class AuthoredMaterial(models.Model):

    title = models.CharField(max_length=200, default=u"")
    text = models.TextField(default=u"")
    author = models.ForeignKey(User)

    summary = models.TextField(default=u"")

    learning_goals = AutoCreateManyToManyField(LearningGoal)
    keywords = AutoCreateManyToManyField(Keyword)
    subjects = models.ManyToManyField(GeneralSubject)
    grade_level = models.ForeignKey(GradeLevel, null=True)
    language = models.ForeignKey(Language, null=True)

    is_new = models.BooleanField(default=True)


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
