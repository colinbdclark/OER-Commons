from curriculum.models import AlignmentTag
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from zope.cachedescriptors.property import Lazy
import re


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
        #noinspection PyUnresolvedReferences
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
        permissions = (
            ("can_manage", u"Can manage evaluations"),
        )
        ordering = ["id"]


class RubricScoreValue(ScoreValue):

    rubric = models.ForeignKey(Rubric, related_name="score_values")

    def __unicode__(self):
        #noinspection PyUnresolvedReferences
        return u"%s - %s" % (self.rubric, self.get_value_display())

    class Meta:
        ordering = ["rubric", "id"]


class Score(models.Model):

    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    confirmed = models.BooleanField(default=False)

    class Meta:
        abstract = True


class RubricScore(Score):

    score = models.ForeignKey(RubricScoreValue)
    rubric = models.ForeignKey(Rubric)


class StandardAlignmentScoreValue(ScoreValue):
    pass


class StandardAlignmentScore(Score):

    score = models.ForeignKey(StandardAlignmentScoreValue)
    alignment_tag = models.ForeignKey(AlignmentTag)


class EvaluatedItemMixin(object):

    EVALUATION_SCORE_ATTRIBUTE_RE = re.compile(r"^evaluation_score_rubric_(\d)$")

    @Lazy
    def evaluations_number(self):
        content_type = ContentType.objects.get_for_model(self)
        user_ids = set()
        for model in (StandardAlignmentScore, RubricScore):
            user_ids.update(
                model.objects.filter(
                    content_type=content_type,
                    object_id=self.pk,
                    confirmed=True,
                ).values_list("user__id", flat=True).distinct()
            )
        return len(user_ids)


    @Lazy
    def evaluation_scores(self):
        scores = {}
        content_type = ContentType.objects.get_for_model(self)
        alignment_scores = StandardAlignmentScore.objects.filter(
            content_type=content_type,
            object_id=self.pk,
            confirmed=True,
        )
        if alignment_scores.exists():
            scores[0] = alignment_scores.aggregate(
                models.Avg("score__value")
            )["score__value__avg"]

        for rubric in Rubric.objects.all():
            rubric_scores = RubricScore.objects.filter(
                content_type=content_type,
                object_id=self.pk,
                confirmed=True,
                rubric=rubric,
            )
            if rubric_scores.exists():
                scores[rubric.id] = rubric_scores.aggregate(
                    models.Avg("score__value")
                )["score__value__avg"]
        return scores

    @property
    def evaluated_rubrics(self):
        return sorted([k for k, v in self.evaluation_scores.items() if v is not None])

    def __getattr__(self, name):
        r = self.EVALUATION_SCORE_ATTRIBUTE_RE.search(name)
        if r:
            rubric_id = int(r.groups()[0])
            try:
                return self.evaluation_scores[rubric_id]
            except KeyError:
                raise AttributeError()
        #noinspection PyUnresolvedReferences
        return super(EvaluatedItemMixin, self).__getattr__(name)


def get_rubric_choices():
    choices = [
        (0, u"Degree of Alignment"),
    ]
    choices += list(Rubric.objects.values_list("id", "name"))
    return choices
