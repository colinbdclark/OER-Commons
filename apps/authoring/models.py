from django.contrib.auth.models import User
from django.db import models
import os


class AuthoredMaterial(models.Model):

    title = models.CharField(max_length=200, default=u"")
    text = models.TextField(default=u"")
    author = models.ForeignKey(User)

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
