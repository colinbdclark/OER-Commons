from django.db import models


class StudentLevel(models.Model):

    title = models.CharField(max_length=100)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ("id",)
