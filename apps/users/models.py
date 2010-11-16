from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from materials.models.common import GradeLevel


MEMBER_ROLES = (
    (u'instructor', _(u'Instructor')),
    (u'student', _(u'Student')),
    (u'self_affiliated', _(u'Self Learner')),
    (u'researcher', _(u'Researcher')),
    (u'oer_administrator', _(u'Administrator')),
    (u'content_provider', _(u'Content provider')),
)


class Profile(models.Model):

    user = models.OneToOneField(User)

    principal_id = models.CharField(max_length=20)

    homepage = models.URLField(max_length=200, blank=True, default=u"",
                               verbose_name=_(u"Homepage"))

    institution = models.CharField(max_length=200, blank=True, default=u"",
                                   verbose_name=_("Institution"))

    institution_url = models.URLField(max_length=200, blank=True, default=u"",
                                      verbose_name=_("Institution URL"))

    grade_level = models.ManyToManyField(GradeLevel, blank=False,
                                         verbose_name=_(u"Grade level"))

    department = models.TextField(blank=True, default=u"",
                                  verbose_name=_(u"Department"))

    specializations = models.TextField(blank=True, default=u"",
                                       verbose_name=u"Specializations")

    state = models.CharField(max_length=200, blank=True, default=u"",
                             verbose_name=_(u"State or province"))

    biography = models.TextField(blank=True, default=u"",
                                 verbose_name=_(u"Biography"))

    why_interested = models.TextField(blank=True, default=u"",
                          verbose_name=_(u"Why are you interested in open "
                                          "educational resources?"))

    publish_portfolio = models.BooleanField(default=False,
                                    verbose_name=_(u"Allow others to see "
                                                    "you portfolio?"))

    publish_profile = models.BooleanField(default=False,
                              verbose_name=_(u"Allow others to see "
                                              "you profile?"))

    role = models.CharField(max_length=20, blank=True, choices=MEMBER_ROLES,
                            verbose_name=_(u"Role"))
