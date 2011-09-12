# -*- coding: utf-8 -*-

import os
from random import choice

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from users.tests.utils import TestDataGenerator
from users.views.forms import (UserInfoForm, ChangePasswordForm, GeographyForm,
    RolesForm, AboutMeForm, AvatarForm)
from users.models import StudentLevel


class UserInfoFormTest(TestCase, TestDataGenerator):

    fixtures = ['users_data.json']

    def get_user_info_data(self):
        # Returns dict with user data.
        data = self.get_full_name()
        data['email'] = self.get_test_userdata()['email']
        return data

    def test_success(self):
        # Test that form valid with correct data.
        form = UserInfoForm(self.get_user_info_data())

        self.assertTrue(form.is_valid())

        # Test form success message.
        form.save()
        self.assertEqual(form.success_mesage, UserInfoForm.success_mesage)

    def test_first_name_required(self):
        # Test that form invalid without first name.
        data = self.get_user_info_data()
        data.pop('first_name')
        form = UserInfoForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['first_name'].errors,
                         [u'This field is required.'])

        # Test from error message.
        self.assertEqual(form.error_message, UserInfoForm.error_message)

    def test_last_name_required(self):
        # Test that form invalid without last name.
        data = self.get_user_info_data()
        data.pop('last_name')
        form = UserInfoForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['last_name'].errors,
                         [u'This field is required.'])

    def test_email_required(self):
        # Test that form invalid without email.
        data = self.get_user_info_data()
        data.pop('email')
        form = UserInfoForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['email'].errors,
                         [u'This field is required.'])

    def test_email_already_used(self):
        # Test that form is invalid with email that already used.
        data = self.get_user_info_data()
        data['email'] = 'john@example.com'

        user = User.objects.get(username='testuser2')
        form = UserInfoForm(data, instance=user)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['email'].errors,
                         [u'This email address is used by another user.'])


class ChangePasswordFormTest(TestCase, TestDataGenerator):

    fixtures = ['users_data.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')

    def test_success(self):
        # Test that form valid with correct data.
        password = self.get_test_password()
        data = {
            u'current_password': u'password',
            u'new_password': password,
            u'confirm_new_password': password
        }
        form = ChangePasswordForm(data, instance=self.user)

        self.assertTrue(form.is_valid())

        # Test form success message.
        form.save()
        self.assertEqual(form.success_message,
                         ChangePasswordForm.success_message)

    def test_clean_current_password(self):
        # Test that currnent password is valid.
        password = self.get_test_password()
        data = {
            u'current_password': u'wrong_password',
            u'new_password': password,
            u'confirm_new_password': password
        }
        form = ChangePasswordForm(data, instance=self.user)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['current_password'].errors,
                         [u'Wrong password'])

    def test_clean_confirm_new_password(self):
        # Test that both of new passwords are match.
        data = {
            u'current_password': u'wrong_password',
            u'new_password': self.get_test_password(),
            u'confirm_new_password': self.get_test_password()
        }
        form = ChangePasswordForm(data, instance=self.user)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['confirm_new_password'].errors,
                         [u'The two passwords do not match.'])


class AvatarFormTest(TestCase):

    def test_success(self):
        # Test that form valid with correct data.
        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.png'
        )
        upload_file = open(test_file_path, 'rb')
        files = {
            u'file': SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        form = AvatarForm({}, files)

        self.assertTrue(form.is_valid())


class GeographyFormTest(TestCase):

    fixtures = ['users_data.json']

    def setUp(self):
        user = User.objects.get(username='testuser')
        self.profile = user.get_profile()

    def test_success(self):
        # Test that form valid with correct data.
        data = {
            u'country': u'US',
            u'us_state': u'NJ',
            u'connect_with': u'world'
        }
        form = GeographyForm(data, instance=self.profile)

        self.assertTrue(form.is_valid())

        # Test form success message.
        form.save()
        self.assertEqual(form.success_message, GeographyForm.success_message)

    def test_clean_method(self):
        # Test that clean method set us_state as none if country is not US.
        data = {
            u'country': u'RU',
            u'connect_with': u'world'
        }
        form = GeographyForm(data, instance=self.profile)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['us_state'], None)


class RolesFormTest(TestCase, TestDataGenerator):

    fixtures = ['users_data.json']

    def setUp(self):
        user = User.objects.get(username='testuser')
        self.profile = user.get_profile()
        self.number_of_levels = StudentLevel.objects.all().count()

    def test_success_simple(self):
        # Test that form is valid with simple roles.
        role_ids = range(4, 14)
        data = {
            u'roles': [u'%s' % choice(role_ids)]
        }
        form = RolesForm(data, instance=self.profile)
        self.assertTrue(form.is_valid())

        # Test form clean method.
        self.assertEqual(form.cleaned_data['educator_student_levels'], [])

        # Test form success message.
        form.save()
        self.assertEqual(form.success_message, RolesForm.success_message)

    def test_success_educator(self):
        # Test that form is valid with educator roles.
        educator_role_ids = range(1, 4)
        data = {
            u'roles': [u'%s' % choice(educator_role_ids)]
        }
        form = RolesForm(data, instance=self.profile)
        self.assertTrue(form.is_valid())

        # Test educator details.
        educator_student_levels_ids = range(1, self.number_of_levels)
        data['educator_student_levels'] = [
            u'%s' % choice(educator_student_levels_ids)
        ]
        form = RolesForm(data, instance=self.profile)
        self.assertTrue(form.is_valid())

        # Test educator subjects.
        data['educator_subjects'] = u'maths, physics'
        form = RolesForm(data, instance=self.profile)
        self.assertTrue(form.is_valid())


class AboutMeFormTest(TestCase, TestDataGenerator):

    fixtures = ['users_data.json']

    def setUp(self):
        user = User.objects.get(username='testuser')
        self.profile = user.get_profile()

    def test_success(self):
        # Test that form valid with correct data.
        data = {
            u'skype_id': u'test_skype_id',
            u'about_me': u'Test about text.',
            u'twitter_id': u'test_twitter_id',
            u'website_url': u'http://google.com',
            u'facebook_id': u'testfacebookid'
        }
        form = AboutMeForm(data, instance=self.profile)

        self.assertTrue(form.is_valid())

        # Test form success message.
        form.save()
        self.assertEqual(form.success_message, AboutMeForm.success_message)

    def test_invalid_url(self):
        # Test that form is invalid with wrond url.
        data = {
            u'skype_id': u'test_skype_id',
            u'about_me': u'Test about text.',
            u'twitter_id': u'test_twitter_id',
            u'website_url': u'woring_url',
            u'facebook_id': u'testfacebookid'
        }
        form = AboutMeForm(data, instance=self.profile)

        self.assertFalse(form.is_valid())

    def test_clean_facebook_id_with_username(self):
        # That clean facebook id method with facebook username.
        data = {
            u'facebook_id': u'testfacebookid'
        }
        form = AboutMeForm(data, instance=self.profile)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['facebook_id'], data['facebook_id'])

    def test_clean_facebook_id_with_short_url(self):
        # That clean facebook id method with facebook profile url.
        data = {
            u'facebook_id': u'https://www.facebook.com/testfacebookid'
        }
        form = AboutMeForm(data, instance=self.profile)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['facebook_id'], u'testfacebookid')

    def test_clean_facebook_id_with_full_url(self):
        # That clean facebook id method with facebook profile url with user id.
        user_id = self.get_str_number(15)
        data = {
            u'facebook_id': u'http://www.facebook.com/profile.php?id=%s' % user_id
        }
        form = AboutMeForm(data, instance=self.profile)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form['facebook_id'].errors,
            [u'Enter a valid value.',
             u'Ensure this value has at most 50 characters (it has 54).']
        )

    def test_clean_twitter_id_with_username(self):
        # That clean twitter id method with twitter username.
        data = {
            u'twitter_id': u'test_twitter_id'
        }
        form = AboutMeForm(data, instance=self.profile)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['twitter_id'], data['twitter_id'])

    def test_clean_twitter_id_with_url(self):
        # That clean twitter id method with twitter profile URL.

        data = {
            u'twitter_id': u'http://twitter.com/#!/test_twitter_id'
        }
        form = AboutMeForm(data, instance=self.profile)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['twitter_id'], u'test_twitter_id')
