# -*- coding: utf-8 -*-

import os
from random import choice

import faker

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse

from sorl.thumbnail.shortcuts import delete

from users.views.forms import (UserInfoForm, ChangePasswordForm, GeographyForm,
    RolesForm, AboutMeForm)
from users.models import Role
from geo.models import Country
from users.tests.utils import TestDataGenerator


class TestLoginMixin(object):

    fixtures = ['users_data.json']

    def login(self):
        data = {
            'username': 'testuser',
            'password': 'password'
        }
        self.client.post(reverse('users:login'), data)


class ProfileViewTest(TestCase, TestLoginMixin):

    def setUp(self):
        self.profile_url = reverse('users:profile')

    def test_login_required(self):
        # Test view without loggin in.
        next_url = '/login?next=%s' % self.profile_url

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

    def test_success(self):
        # Test than profile view works correctly.
        self.login()
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertContains(response, 'testfacebook')
        self.assertContains(response, 'Test about text.')
        self.assertContains(response, 'testtwitter')


class ProfileEditTest(TestCase, TestLoginMixin, TestDataGenerator):

    def setUp(self):
        self.profile_edit_url = reverse('users:profile_edit')
        self.unfilled_profile_edit_url = '%s?unfilled=yes' % self.profile_edit_url
        self.geography_url = reverse('users:profile_geography')
        self.roles_url = reverse('users:profile_roles')
        self.about_url = reverse('users:profile_about')

    def get_profile(self):
        user = User.objects.get(username='testuser')
        return user.get_profile()

    def test_login_required(self):
        # Test view without loggin in.
        next_url = '/login?next=%s' % self.profile_edit_url

        response = self.client.get(self.profile_edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

    def test_get(self):
        # Test that edit view works correctly with GET request.
        self.login()
        response = self.client.get(self.profile_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile-edit.html')

    def test_get_unfilled_country_none(self):
        # Test GET request with unfilled arguments and country is None.
        profile = self.get_profile()
        profile.country = None
        profile.save()

        self.login()

        response = self.client.get(self.unfilled_profile_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.geography_url))

    def test_get_unfilled_country_us(self):
        # Test GET request with unfilled arguments and country is None.
        country = Country.objects.get(code='US')
        profile = self.get_profile()
        profile.country = country
        profile.us_state = None
        profile.save()

        self.login()

        response = self.client.get(self.unfilled_profile_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.geography_url))

    def test_get_unfilled_roles(self):
        # Test GET request with unfilled arguments and roles is None.
        profile = self.get_profile()
        profile.roles.clear()

        self.login()

        response = self.client.get(self.unfilled_profile_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.roles_url))

    def test_get_unfilled_educator_student_levels_none(self):
        # Test GET request with educator student levels is None.
        role = Role.objects.get(title='Educator')
        profile = self.get_profile()
        profile.roles.add(role)
        profile.educator_student_levels.clear()

        self.login()

        response = self.client.get(self.unfilled_profile_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.roles_url))

    def test_get_unfilled_without_twitter(self):
        # Test GET request with unfilled arguments and twitter is None.
        profile = self.get_profile()
        profile.twitter_id = None
        profile.save()

        self.login()

        response = self.client.get(self.unfilled_profile_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.about_url))

    def test_post_success_user_info(self):
        # Test POST request success with UserInfoForm form.
        data = {
            u'first_name': faker.name.first_name(),
            u'last_name': faker.name.last_name(),
            u'email': faker.internet.email(),
            u'user-info': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.geography_url))

    def test_ajax_post_success_user_info(self):
        # Test ajax POST request success with UserInfoForm form.
        data = {
            u'first_name': faker.name.first_name(),
            u'last_name': faker.name.last_name(),
            u'email': faker.internet.email(),
            u'user-info': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, UserInfoForm.success_message)

    def test_post_unsuccess_user_info(self):
        # Test POST request unsuccess with invalid UserInfoForm form.
        data = {
            u'first_name': faker.name.first_name(),
            u'last_name': faker.name.last_name(),
            u'email': u'',
            u'user-info': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, UserInfoForm.error_message)

    def test_ajax_post_unsuccess_user_info(self):
        # Test ajax POST request unsuccess with invalid UserInfoForm form.
        data = {
            u'first_name': faker.name.first_name(),
            u'last_name': faker.name.last_name(),
            u'email': u'',
            u'user-info': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'error')
        self.assertContains(response, UserInfoForm.error_message)

    def test_post_success_change_password(self):
        # Test POST request success with ChangePasswordForm form.
        password = self.get_test_password()
        data = {
            u'current_password': u'password',
            u'new_password': password,
            u'confirm_new_password': password,
            u'change-password': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         u'OER Commons: Password Changed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ChangePasswordForm.success_message)

    def test_ajax_post_success_change_password(self):
        # Test ajax POST request success with ChangePasswordForm form.
        password = self.get_test_password()
        data = {
            u'current_password': u'password',
            u'new_password': password,
            u'confirm_new_password': password,
            u'change-password': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         u'OER Commons: Password Changed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, ChangePasswordForm.success_message)

    def test_post_unsuccess_change_password(self):
        # Test POST request unsuccess with invalid ChangePasswordForm form.
        password = self.get_test_password()
        data = {
            u'current_password': u'password',
            u'new_password': password,
            u'confirm_new_password': u'',
            u'change-password': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ChangePasswordForm.error_message)

    def test_ajax_post_unsuccess_change_password(self):
        # Test ajax POST request unsuccess with invalid ChangePasswordForm form.
        password = self.get_test_password()
        data = {
            u'current_password': u'password',
            u'new_password': password,
            u'confirm_new_password': u'',
            u'change-password': u'Save'
        }
        self.login()
        response = self.client.post(self.profile_edit_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'error')
        self.assertContains(response, ChangePasswordForm.error_message)


class AvatarUpdateViewTest(TestCase, TestLoginMixin):

    def setUp(self):
        self.update_avatar_url = reverse('users:profile_avatar_update')

    def get_profile(self):
        user = User.objects.get(username='testuser')
        return user.get_profile()

    def test_login_required(self):
        # Test view without loggin in.
        next_url = '/login?next=%s' % self.update_avatar_url

        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.jpg'
        )
        image_file = open(test_file_path, 'r')
        response = self.client.post(self.update_avatar_url,
                                    {'file': image_file})
        image_file.close()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

    def test_success_jpg(self):
        # Test view with .jpg image
        profile = self.get_profile()

        self.assertFalse(profile.avatar)

        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.jpg'
        )
        image_file = open(test_file_path, 'r')
        self.login()
        response = self.client.post(self.update_avatar_url,
                                    {'file': image_file})
        image_file.close()

        profile = self.get_profile()
        filename = '%i%s' % (profile.user.id, u'.jpg')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, u'Your picture is saved.')
        self.assertTrue(profile.avatar.url.endswith(filename))

        delete(profile.avatar)

    def test_success_png(self):
        # Test view with .png image
        profile = self.get_profile()

        self.assertFalse(profile.avatar)

        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.png'
        )
        image_file = open(test_file_path, 'r')
        self.login()
        response = self.client.post(self.update_avatar_url,
                                    {'file': image_file})
        image_file.close()
        profile = self.get_profile()
        filename = '%i%s' % (profile.user.id, u'.png')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, u'Your picture is saved.')
        self.assertTrue(profile.avatar.url.endswith(filename))

        delete(profile.avatar)

    def test_success_gif(self):
        # Test view with .gif image
        profile = self.get_profile()

        self.assertFalse(profile.avatar)

        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.gif'
        )
        image_file = open(test_file_path, 'r')
        self.login()
        response = self.client.post(self.update_avatar_url,
                                    {'file': image_file})
        image_file.close()
        profile = self.get_profile()
        filename = '%i%s' % (profile.user.id, u'.gif')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, u'Your picture is saved.')
        self.assertTrue(profile.avatar.url.endswith(filename))

        delete(profile.avatar)

    def test_success_no_extension(self):
        # Test view with image without extension.
        profile = self.get_profile()

        self.assertFalse(profile.avatar)

        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file'
        )
        image_file = open(test_file_path, 'r')
        self.login()
        response = self.client.post(self.update_avatar_url,
                                    {'file': image_file})
        image_file.close()
        profile = self.get_profile()
        filename = '%i%s' % (profile.user.id, u'')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, u'Your picture is saved.')
        self.assertTrue(profile.avatar.url.endswith(filename))

        delete(profile.avatar)

    def test_success_with_avatar(self):
        # Test view with exist profile avatar.
        self.login()

        # Add image to profile.
        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.gif'
        )
        image_file = open(test_file_path, 'r')
        self.client.post(self.update_avatar_url, {'file': image_file})
        image_file.close()

        profile = self.get_profile()
        self.assertEqual(profile.avatar.url, '/media/upload/avatars/1.gif')

        # Change it and check that was changed.
        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.png'
        )
        image_file = open(test_file_path, 'r')
        self.client.post(self.update_avatar_url, {'file': image_file})
        image_file.close()

        profile = self.get_profile()
        self.assertEqual(profile.avatar.url, '/media/upload/avatars/1.png')

        delete(profile.avatar)

    def test_unsuccess(self):
        # Test with empty file.
        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/wrong_image_file.png'
        )
        image_file = open(test_file_path, 'r')
        self.login()
        response = self.client.post(self.update_avatar_url,
                                    {'file': image_file})
        image_file.close()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'error')
        self.assertContains(
            response,
            u'''The submitted file is empty.'''
        )

        # Test with non image file.
        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/wrong_image_file.txt'
        )
        image_file = open(test_file_path, 'r')
        self.login()
        response = self.client.post(self.update_avatar_url,
                                    {'file': image_file})
        image_file.close()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'error')
        self.assertContains(
            response,
            u'Upload a valid image. The file you uploaded was either not an image or a corrupted image.'
        )


class AvatarDeleteViewTest(TestCase, TestLoginMixin):

    def setUp(self):
        self.delete_avatar_url = reverse('users:profile_avatar_delete')
        self.update_avatar_url = reverse('users:profile_avatar_update')

    def get_profile(self):
        user = User.objects.get(username='testuser')
        return user.get_profile()

    def test_login_required(self):
        # Test view without loggin in.
        next_url = '/login?next=%s' % self.delete_avatar_url

        response = self.client.post(self.delete_avatar_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

    def test_success(self):
        # Test than delete avatar view works correctly.
        self.login()
        response = self.client.post(self.delete_avatar_url)

        profile = self.get_profile()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, u'Your picture is deleted.')
        self.assertContains(response, u'/media/images/default-avatar.png')
        self.assertTrue(profile.hide_avatar)

    def test_success_with_avatar(self):
        # Test view with exist profile avatar.
        profile = self.get_profile()
        self.assertFalse(profile.avatar)

        self.login()

        # Add image to profile.
        test_file_path = os.path.join(
            os.path.dirname(__file__), '../fixtures/test_file.png'
        )
        image_file = open(test_file_path, 'r')
        self.client.post(self.update_avatar_url, {'file': image_file})
        image_file.close()

        profile = self.get_profile()
        self.assertEqual(profile.avatar.url, '/media/upload/avatars/1.png')

        # Test that avatar has been delete.
        response = self.client.post(self.delete_avatar_url)
        profile = self.get_profile()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'success')
        self.assertContains(response, u'Your picture is deleted.')
        self.assertContains(response, u'/media/images/default-avatar.png')
        self.assertTrue(profile.hide_avatar)


class GeographyViewTest(TestCase, TestLoginMixin):

    def setUp(self):
        self.roles_url = reverse('users:profile_roles')
        self.geography_url = reverse('users:profile_geography')

    def test_login_required(self):
        # Test view without loggin in.
        next_url = '/login?next=%s' % self.geography_url

        # GET
        response = self.client.get(self.geography_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

        # POST
        data = {
            u'country': u'US',
            u'us_state': u'NJ',
            u'connect_with': u'world'
        }
        response = self.client.post(self.geography_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

    def test_get(self):
        # Test that about view works correctly with get request.
        user = User.objects.get(username='testuser')
        profile = user.get_profile()
        profile.country = None
        profile.save()

        self.login()
        response = self.client.get(self.geography_url,
                                   **{'REMOTE_ADDR': '209.85.148.103'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile-geography.html')

    def test_post(self):
        # Test that view works correctly with POST request.
        data = {
            u'country': u'US',
            u'us_state': u'NJ',
            u'connect_with': u'world'
        }
        self.login()
        response = self.client.post(self.geography_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.roles_url))

    def test_post_form_invalid(self):
        # Test view with ajax POST request and form invalid.
        data = {
            u'country': u'wrong counrty',
            u'us_state': u'NJ',
            u'connect_with': u'world'
        }
        self.login()
        response = self.client.post(self.geography_url, data)

        self.assertContains(response, GeographyForm.error_message)

    def test_ajax_post(self):
        # Test that view works correctly with ajax POST request.
        data = {
            u'country': u'US',
            u'us_state': u'NJ',
            u'connect_with': u'world'
        }
        self.login()
        response = self.client.post(self.geography_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, GeographyForm.success_message)

    def test_ajax_post_form_invalid(self):
        # Test that view works correctly with ajax POST request.
        data = {
            u'country': u'wrong country',
            u'us_state': u'NJ',
            u'connect_with': u'world'
        }
        self.login()
        response = self.client.post(self.geography_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, GeographyForm.error_message)


class RolesViewTest(TestCase, TestLoginMixin):

    def setUp(self):
        self.about_url = reverse('users:profile_about')
        self.roles_url = reverse('users:profile_roles')

    def test_login_required(self):
        # Test view without loggin in.
        next_url = '/login?next=%s' % self.roles_url

        # GET
        response = self.client.get(self.roles_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

        # POST
        educator_role_ids = range(1, 4)
        data = {
            u'roles': [u'%s' % choice(educator_role_ids)]
        }
        response = self.client.post(self.roles_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

    def test_get(self):
        # Test that view works correctly with get request.
        self.login()
        response = self.client.get(self.roles_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile-roles.html')

    def test_post(self):
        # Test that view works correctly with POST request.
        educator_role_ids = range(1, 4)
        data = {
            u'roles': [u'%s' % choice(educator_role_ids)]
        }
        self.login()
        response = self.client.post(self.roles_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.about_url))

    def test_post_form_invalid(self):
        # Test view with ajax POST request and form invalid.
        data = {
            u'roles': u'wrong role'
        }
        self.login()
        response = self.client.post(self.roles_url, data)

        self.assertContains(response, RolesForm.error_message)

    def test_ajax_post(self):
        # Test that view works correctly with ajax POST request.
        educator_role_ids = range(1, 4)
        data = {
            u'roles': [u'%s' % choice(educator_role_ids)]
        }
        self.login()
        response = self.client.post(self.roles_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, RolesForm.success_message)

    def test_ajax_post_form_invalid(self):
        # Test that view works correctly with ajax POST request.
        data = {
            u'roles': u'wrong role'
        }
        self.login()
        response = self.client.post(self.roles_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, RolesForm.error_message)


class AboutViewTest(TestCase, TestLoginMixin):

    def setUp(self):
        self.profile_url = reverse('users:profile')
        self.about_url = reverse('users:profile_about')

    def test_login_required(self):
        # Test view without loggin in.
        next_url = '/login?next=%s' % self.about_url

        # GET
        response = self.client.get(self.about_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

        # POST
        data = {
            u'skype_id': u'test_skype_id',
            u'about_me': u'Test about text.',
            u'twitter_id': u'test_twitter_id',
            u'website_url': u'http://google.com',
            u'facebook_id': u'testfacebookid'
        }
        response = self.client.post(self.about_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(next_url))

    def test_get(self):
        # Test that about view works correctly with get request.
        self.login()
        response = self.client.get(self.about_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile-about.html')

    def test_post(self):
        # Test that about view works correctly with POST request.
        self.login()
        data = {
            u'skype_id': u'test_skype_id',
            u'about_me': u'Test about text.',
            u'twitter_id': u'test_twitter_id',
            u'website_url': u'http://google.com',
            u'facebook_id': u'testfacebookid'
        }
        response = self.client.post(self.about_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.profile_url))

        # Test than new data was saved in profile.
        response = self.client.get(self.profile_url)
        self.assertContains(response, data['skype_id'])
        self.assertContains(response, data['about_me'])
        self.assertContains(response, data['twitter_id'])
        self.assertContains(response, data['website_url'])
        self.assertContains(response, data['facebook_id'])

    def test_post_form_invalid(self):
        # Test about view with ajax POST request and form invalid.
        self.login()
        data = {
            u'skype_id': u'test_skype_id',
            u'about_me': u'Test about text.',
            u'twitter_id': u'test_twitter_id',
            u'website_url': u'woring_url',
            u'facebook_id': u'testfacebookid'
        }
        response = self.client.post(self.about_url, data)
        self.assertContains(response, AboutMeForm.error_message)

    def test_ajax_post(self):
        # Test that about view works correctly with ajax POST request.
        self.login()
        data = {
            u'skype_id': u'test_skype_id',
            u'about_me': u'Test about text.',
            u'twitter_id': u'test_twitter_id',
            u'website_url': u'http://google.com',
            u'facebook_id': u'testfacebookid'
        }
        response = self.client.post(self.about_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, AboutMeForm.success_message)

    def test_ajax_post_form_invalid(self):
        # Test about view with ajax POST request and form invalid.
        self.login()
        data = {
            u'skype_id': u'test_skype_id',
            u'about_me': u'Test about text.',
            u'twitter_id': u'test_twitter_id',
            u'website_url': u'woring_url',
            u'facebook_id': u'testfacebookid'
        }
        response = self.client.post(self.about_url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, AboutMeForm.error_message)
