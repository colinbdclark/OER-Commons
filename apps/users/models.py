from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from geo.models import Country, USState
from materials.models.common import GradeLevel, AutoCreateManyToManyField
from sorl.thumbnail.shortcuts import get_thumbnail
from users.backend import encrypt_password
import hashlib
import urllib


MEMBER_ROLES = (
    (u'instructor', _(u'Instructor')),
    (u'student', _(u'Student')),
    (u'self_affiliated', _(u'Self Learner')),
    (u'researcher', _(u'Researcher')),
    (u'oer_administrator', _(u'Administrator')),
    (u'content_provider', _(u'Content provider')),
)


ONLY_COUNTRY = "country"
WHOLE_WORLD = "world"
CONNECT_OPTIONS = (
    (ONLY_COUNTRY, u"Connect me only to people in my own country"),
    (WHOLE_WORLD, u"Connect me to learners and educators around the world"),
)


class Role(models.Model):
    
    title = models.CharField(max_length=100)
    is_educator = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ("id",)


class StudentLevel(models.Model):
    
    title = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ("id",)


class EducatorSubject(models.Model):
    
    title = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ("id",)


class Profile(models.Model):

    user = models.OneToOneField(User)

    principal_id = models.CharField(max_length=20)

    avatar = models.ImageField(blank=True, null=True, upload_to="upload/avatars")

    hide_avatar = models.BooleanField(default=False)

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
    
    country = models.ForeignKey(Country, blank=True, null=True)

    us_state = models.ForeignKey(USState, blank=True, null=True)

    connect_with = models.CharField(max_length=20, choices=CONNECT_OPTIONS,
                                    blank=True, null=True)

    # This is an obsolete field. It is replaced with `roles` field now which
    # allows multiple values.
    role = models.CharField(max_length=20, blank=True, choices=MEMBER_ROLES,
                            verbose_name=_(u"Role"))

    roles = models.ManyToManyField(Role, null=True, blank=True)
    
    educator_student_levels = models.ManyToManyField(StudentLevel, null=True,
                                                     blank=True) 

    educator_subjects = AutoCreateManyToManyField(EducatorSubject, null=True,
                                                  blank=True) 
    
    about_me = models.TextField(blank=True, null=True)

    def get_avatar_url(self):
        if self.hide_avatar:
            return settings.DEFAULT_AVATAR
        if self.avatar:
            thumbnail = get_thumbnail(self.avatar,
                                      "%(size)ix%(size)i" % dict(size=settings.AVATAR_SIZE),
                                      crop="center")
            return thumbnail.url
        elif self.user.email:
            try:
                default = "http://%s%s" % (Site.objects.get_current().domain, settings.DEFAULT_AVATAR)
                url = "%s/%s.jpg?%s" % (settings.GRAVATAR_BASE,
                                        hashlib.md5(self.user.email).hexdigest(),
                                        urllib.urlencode({
                                            'size': str(settings.AVATAR_SIZE),
                                            'rating': "g",
                                            'default': default,
                                        }))
            except:
                import traceback
                print traceback.format_exc()
                raise
            return url

        return settings.DEFAULT_AVATAR

    def get_avatar_img(self):
        return mark_safe("""<img src="%(url)s" width="%(size)i" height="%(size)i" />""" % dict(
                            url=self.get_avatar_url(), size=settings.AVATAR_SIZE))


def gen_confirmation_key():
    return User.objects.make_random_password(length=20)


class RegistrationConfirmation(models.Model):

    user = models.ForeignKey(User)
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
                               body, to=[self.user.email])
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

    user = models.ForeignKey(User)
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
                               body, to=[self.user.email])
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
