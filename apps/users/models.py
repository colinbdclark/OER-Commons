from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from materials.models.common import GradeLevel
from users.backend import encrypt_password


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


def gen_confirmation_key():
    return User.objects.make_random_password(length=20)


class RegistrationConfirmation(models.Model):

    user = models.OneToOneField(User)
    key = models.CharField(max_length=20, unique=True)
    confirmed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.key:
            key = gen_confirmation_key()
            while RegistrationConfirmation.objects.filter(key=key).count():
                key = gen_confirmation_key()
            self.key = key
        super(RegistrationConfirmation, self).save(*args, **kwargs)

    def send_confirmation(self):
        url = reverse("users:registration_confirm")
        url = "http://%s%s" % (Site.objects.get_current().domain, url)
        body = render_to_string("users/emails/registration-confirmation.html",
                                   dict(url=url, key=self.key, user=self.user))
        message = EmailMessage(u"Confirm your registration at OER Commons",
                               body, None, [self.user.email])
        message.content_subtype = "html"
        message.send()

    def confirm(self):
        if self.confirmed:
            return False
        self.user.is_active = True
        self.user.save()
        self.confirmed = True
        self.save()
        return True


class ResetPasswordConfirmation(models.Model):

    user = models.OneToOneField(User)
    key = models.CharField(max_length=20, unique=True,
                           default=gen_confirmation_key)
    confirmed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            key = gen_confirmation_key()
            while ResetPasswordConfirmation.objects.filter(key=key).count():
                key = gen_confirmation_key()
            self.key = key
        super(ResetPasswordConfirmation, self).save(*args, **kwargs)


    def send_confirmation(self):
        url = reverse("users:reset_password", kwargs=dict(key=self.key))
        url = "http://%s%s" % (Site.objects.get_current().domain, url)
        body = render_to_string("users/emails/reset-password-confirmation.html",
                                   dict(url=url, user=self.user))
        message = EmailMessage(u"Reset your OER Commons password",
                               body, None, [self.user.email])
        message.content_subtype = "html"
        message.send()

    def confirm(self, password):
        if self.confirmed:
            return False
        self.user.password = encrypt_password(password)
        self.user.save()
        self.confirmed = True
        self.save()
        return True
