from curriculum.models import AlignmentTag
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


SCORES = (
    (3, u"Superior"),
    (2, u"Strong"),
    (1, u"Limited"),
    (0, u"Very Weak"),
    (None, u"Not Applicable"),
)


class ScoreValue(models.Model):

    value = models.PositiveSmallIntegerField(null=True, blank=True,
                                             choices=SCORES)
    description = models.TextField()

    def __unicode__(self):
        return self.get_value_display()

    class Meta:
        abstract = True
        ordering = ["id"]


class Rubric(models.Model):

    name = models.CharField(max_length=200)
    description = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class RubricScoreValue(ScoreValue):

    rubric = models.ForeignKey(Rubric, related_name="score_values")

    def __unicode__(self):
        return u"%s - %s" % (self.rubric, self.get_value_display())

    class Meta:
        ordering = ["rubric", "id"]


class RubricScore(models.Model):

    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    rubric = models.ForeignKey(Rubric)

    score = models.ForeignKey(RubricScoreValue)


class StandardAlignmentScoreValue(ScoreValue):
    pass


class StandardAlignmentScore(models.Model):

    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    alignment_tag = models.ForeignKey(AlignmentTag)

    score = models.ForeignKey(StandardAlignmentScoreValue)
