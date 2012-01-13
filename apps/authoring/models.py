from django.contrib.auth.models import User
from django.db import models


class AuthoredMaterial(models.Model):

    title = models.CharField(max_length=200, default=u"")
    text = models.TextField(default=u"")
    author = models.ForeignKey(User)

    is_new = models.BooleanField(default=True)


class Image(models.Model):

    image = models.ImageField(upload_to="authoring/images/")
    material = models.ForeignKey(AuthoredMaterial)
