# -*- coding: utf-8 -*-

import os
import re
from random import choice

from mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.conf import settings

from sorl.thumbnail.shortcuts import delete

from users.models import (Role, EducatorSubject, gen_confirmation_key,
    RegistrationConfirmation, ResetPasswordConfirmation, StudentLevel)
from geo.models import Country, USState

from users.tests.utils import TestDataGenerator


class RoleTest(TestCase):

    def test_educatior_roles(self):
        # Test that educator roles are exist.
        role_ids = range(1, 4)
        role = Role.objects.filter(id=choice(role_ids))

        self.assertTrue(role.exists())
        self.assertTrue(role[0].is_educator)

    def test_student_roles(self):
        # Test that student roles are exist.
        role_ids = range(4, 14)
        role = Role.objects.filter(id=choice(role_ids))

        self.assertTrue(role.exists())
        self.assertFalse(role[0].is_educator)


class EducatorSubjectTest(TestCase):

    def setUp(self):
        EducatorSubject.objects.create(title=u'test subject')

    def test_subject(self):
        # Test that student roles is exist.
        subject = EducatorSubject.objects.filter(title=u'test subject')

        self.assertTrue(subject.exists())
        self.assertEqual(subject[0].title, u'test subject')


class ProfileTest(TestCase):

    fixtures = ['users_data.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.number_of_levels = StudentLevel.objects.all().count()

    def fill_profile(self):
        # Fill profile for tests.
        role_ids = range(1, 4)
        educator_student_levels_ids = range(1, self.number_of_levels)
        country = Country.objects.get(code='US')
        us_state = USState.objects.get(name='Alabama')
        educator_subject = EducatorSubject.objects.create(title=u'Chemistry')

        profile = self.user.get_profile()
        profile.roles.add(choice(role_ids))
        profile.educator_student_levels.add(choice(educator_student_levels_ids))
        profile.educator_subjects.add(educator_subject.id)
        profile.country = country
        profile.us_state = us_state
        profile.save()

        return profile

    def test_profile(self):
        # Test profile model.
        profile = self.user.get_profile()

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.about_me, u'Test about text.')
        self.assertEqual(profile.facebook_id, u'testfacebook')
        self.assertEqual(profile.twitter_id, u'testtwitter')

    def test_facebook_validator(self):
        # Test facebook validator.
        profile = self.user.get_profile()
        profile.facebook_id = 't#st'

        try:
            profile.full_clean()
        except ValidationError:
            pass
        else:
            self.fail('Validator passed incorect value.')

    def test_twitter_validator(self):
        # Test twitter validator.
        profile = self.user.get_profile()
        profile.twitter_id = 't#st'

        try:
            profile.full_clean()
        except ValidationError:
            pass
        else:
            self.fail('Validator passed incorect value.')

    def test_get_avatar_url_hide_avatar(self):
        # Test get_avatar_url method if hide_avatar is True.
        profile = self.user.get_profile()
        profile.hide_avatar = True
        profile.save()

        self.assertEqual(profile.get_avatar_url(),
                         u'/media/images/default-avatar.png')

    def test_get_avatar_url(self):
        # Test get_avatar_url method if avatar is True.
        test_file_path = os.path.join(
            os.path.dirname(__file__), 'fixtures/test_file.jpg'
        )
        image_file = open(test_file_path, 'r')
        profile = self.user.get_profile()
        profile.avatar.save('test_avatar.jpg', ContentFile(image_file.read()))
        url = profile.get_avatar_url()

        url_regex = re.compile(
            r'^/media/cache/[a-f0-9]{2}/[a-f0-9]{2}/[a-f0-9]{32}\.jpg$'
        )
        self.assertTrue(url_regex.match(url))

        delete(profile.avatar)

    def test_get_avatar_url_email(self):
        # Test get_avatar_url method if user.email is True.
        profile = self.user.get_profile()
        url = profile.get_avatar_url()

        self.assertTrue(url.startswith(
            u'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6.jpg')
        )

    def test_avatar_url_all_none(self):
        # Test get_avatar_url method if none of ifs was handled.
        profile = self.user.get_profile()
        profile.user.email = u''
        profile.user.save()

        self.assertEqual(profile.get_avatar_url(),
                         u'/media/images/default-avatar.png')

    def test_get_avatar_img(self):
        # Test get_avatar_img method.
        profile = self.user.get_profile()
        result = profile.get_avatar_img()
        size = settings.AVATAR_SIZE

        self.assertTrue(result.startswith(
            '<img src="http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6.jpg'
            )
        )
        self.assertTrue(result.endswith(
            'size=%(size)i" width="%(size)i" height="%(size)i" />' % dict(size=size)
            )
        )

    def test_total_fields(self):
        # Test total_fields property.
        profile = self.fill_profile()

        self.assertEqual(profile.total_fields, 10)

    def test_filled_fields(self):
        # Test filled_fields property.
        profile = self.fill_profile()

        self.assertTrue(self.user.first_name)
        self.assertTrue(self.user.last_name)
        self.assertTrue(profile.country)
        self.assertTrue(profile.connect_with)
        self.assertTrue(profile.roles.all().exists())
        self.assertTrue(profile.roles.filter(is_educator=True).exists())
        self.assertTrue(profile.about_me)
        self.assertTrue(profile.website_url or profile.facebook_id or profile.twitter_id or profile.skype_id)
        self.assertEqual(profile.filled_fields, 10)

    def test_completeness_full(self):
        # Test completeness property.
        profile = self.fill_profile()

        self.assertEqual(profile.completeness, 100)

    def test_completeness_90(self):
        # Test completeness property.
        profile = self.fill_profile()
        profile.about_me = None
        profile.save()

        self.assertEqual(profile.completeness, 90)


class GenConfirmationKeyTest(TestCase):

    def test_confirmation_key(self):
        # Test confirmation key lenght.
        key = gen_confirmation_key()
        self.assertEqual(len(key), 20)


class RegistrationConfirmationTest(TestCase):

    fixtures = ['users_data.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.key = gen_confirmation_key()

    def test_save_method_with_key(self):
        # Test that confirmation creates correctly.
        confirmation = RegistrationConfirmation.objects.create(
            user=self.user,
            key=self.key,
            confirmed=False
        )
        self.assertEqual(confirmation.key, self.key)
        self.assertEqual(confirmation.user, self.user)
        self.assertFalse(confirmation.confirmed)

    def test_save_method_non_key(self):
        # Test that confirmation creates correctly without key.
        confirmation = RegistrationConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        self.assertTrue(confirmation.key)
        self.assertEqual(confirmation.user, self.user)
        self.assertFalse(confirmation.confirmed)

    @patch('users.models.gen_confirmation_key')
    def test_save_method_key_exist(self, gen_confirmation_key_mock):
        # Test that confirmation creates correctly with existed key.
        RegistrationConfirmation.objects.create(
            user=self.user,
            key=self.key,
            confirmed=False
        )
        results = [
            gen_confirmation_key(),
            self.key,
        ]

        def side_effect(*args, **kwargs):
            return results.pop()

        gen_confirmation_key_mock.side_effect = side_effect

        confirmation = RegistrationConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        self.assertTrue(confirmation.key)
        self.assertNotEqual(confirmation.key, self.key)
        self.assertEqual(confirmation.user, self.user)
        self.assertFalse(confirmation.confirmed)

    def test_send_confirmation(self):
        # Test send_confirmation method.
        confirmation = RegistrationConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        confirmation.send_confirmation()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(mail.outbox[0].subject,
                         u'Confirm your registration at OER Commons')

    def test_confirm_method_confirmed(self):
        # Test confirm method for confirmed confirmation
        confirmation = RegistrationConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        confirmation.confirmed = True
        confirmation.save()

        self.assertFalse(confirmation.confirm())

    def test_confirm_method(self):
        # Test confirm method works correctly.
        user = User.objects.get(username='testuser')
        user.is_active = False
        user.save()

        confirmation = RegistrationConfirmation.objects.create(
            user=user,
            confirmed=False
        )
        result = confirmation.confirm()

        self.assertTrue(result)
        self.assertTrue(confirmation.confirmed)
        self.assertTrue(user.is_active)


class ResetPasswordConfirmationTest(TestCase, TestDataGenerator):

    fixtures = ['users_data.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.key = gen_confirmation_key()

    def test_save_method_with_key(self):
        # Test that confirmation creates correctly.
        confirmation = ResetPasswordConfirmation.objects.create(
            user=self.user,
            key=self.key,
            confirmed=False
        )
        self.assertEqual(confirmation.key, self.key)
        self.assertEqual(confirmation.user, self.user)
        self.assertFalse(confirmation.confirmed)

    def test_save_method_non_key(self):
        # Test that confirmation creates correctly without key.
        confirmation = ResetPasswordConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        self.assertTrue(confirmation.key)
        self.assertEqual(confirmation.user, self.user)
        self.assertFalse(confirmation.confirmed)

    @patch('users.models.gen_confirmation_key')
    def test_save_method_key_exist(self, gen_confirmation_key_mock):
        # Test that confirmation creates correctly with existed key.
        ResetPasswordConfirmation.objects.create(
            user=self.user,
            key=self.key,
            confirmed=False
        )
        results = [
            gen_confirmation_key(),
            self.key,
        ]

        def side_effect(*args, **kwargs):
            return results.pop()

        gen_confirmation_key_mock.side_effect = side_effect

        confirmation = ResetPasswordConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        self.assertTrue(confirmation.key)
        self.assertNotEqual(confirmation.key, self.key)
        self.assertEqual(confirmation.user, self.user)
        self.assertFalse(confirmation.confirmed)

    def test_send_confirmation(self):
        # Test send_confirmation method.
        confirmation = ResetPasswordConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        confirmation.send_confirmation()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(mail.outbox[0].subject,
                         u'Reset your OER Commons password')

    def test_confirm_method_confirmed(self):
        # Test confirm method for confirmed confirmation
        confirmation = ResetPasswordConfirmation.objects.create(
            user=self.user,
            confirmed=False
        )
        confirmation.confirmed = True
        confirmation.save()
        password = self.get_test_password()

        self.assertFalse(confirmation.confirm(password))

    def test_confirm_method(self):
        # Test confirm method works correctly.
        user = User.objects.get(username='testuser')
        user.is_active = False
        user.save()

        confirmation = ResetPasswordConfirmation.objects.create(
            user=user,
            confirmed=False
        )
        password = self.get_test_password()
        result = confirmation.confirm(password)

        self.assertTrue(result)
        self.assertTrue(confirmation.confirmed)
