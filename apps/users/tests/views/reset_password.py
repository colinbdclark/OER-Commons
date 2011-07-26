# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail

import faker

from users.models import ResetPasswordConfirmation
from users.views.reset_password import InitResetPasswordForm, ResetPasswordForm
from users.tests.utils import TestDataGenerator


class InitResetPasswordFormTest(TestCase, TestDataGenerator):

    fixtures = ['users_test_data.json']

    def test_success_with_email(self):
        # Test that form is valid with correct email.
        email = 'john@example.com'
        form = InitResetPasswordForm({'username_or_email': email})
        self.assertTrue(form.is_valid())

    def test_success_with_username(self):
        # Test that form is valid with correct username.
        email = 'testuser'
        form = InitResetPasswordForm({'username_or_email': email})
        self.assertTrue(form.is_valid())

    def test_email_not_exist(self):
        # Test that user with this email is not registered.
        data = self.get_test_userdata()
        form_data = {'username_or_email': data['email']}
        form = InitResetPasswordForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form['username_or_email'].errors,
            [u'User account with this email is not registered. <a href="#">Register now.</a>']
        )

    def test_username_not_exist(self):
        # Test that user with this username is not registered.
        username = faker.internet.user_name()
        form = InitResetPasswordForm({'username_or_email': username})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form['username_or_email'].errors,
            [u'User account with this username is not registered. <a href="#">Register now.</a>']
        )


class ResetPasswordFormTest(TestCase, TestDataGenerator):

    def test_success(self):
        # Test that form is valid with correct passwords.
        password = self.get_test_password()
        passwords = {
            'password': password,
            'confirm_password': password
        }
        form = ResetPasswordForm(passwords)
        self.assertTrue(form.is_valid())

    def test_password_length(self):
        # Test that password length is valid.
        password = self.get_test_password(4)
        passwords = {
            'password': password,
            'confirm_password': password
        }

        form = ResetPasswordForm(passwords)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form['password'].errors,
            [u'Ensure this value has at least 5 characters (it has %d).' % len(password)]
        )

    def test_passwords_dont_match(self):
        # Test that two passwords do not match.
        passwords = {
            'password': self.get_test_password(),
            'confirm_password': self.get_test_password()
        }

        form = ResetPasswordForm(passwords)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['confirm_password'].errors,
                         [u'The two passwords do not match.'])


class InitViewTest(TestCase, TestDataGenerator):

    fixtures = ['users_test_data.json']

    def setUp(self):
        self.reset_password_init = reverse('users:reset_password_init')
        self.fronpage_url = reverse('frontpage')

    def test_rendered_template(self):
        # Test that page was rendered with correct template.
        response = self.client.get(reverse('users:reset_password_init'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/reset-password-init.html')

    def test_user_is_authenticated(self):
        # Test than view redirect to front page if user is already authenticated.
        login = reverse('users:login')
        login_data = {
            'username': 'john@example.com',
            'password': 'password',
        }
        response = self.client.post(login, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.fronpage_url))

        response = self.client.get(reverse('users:reset_password_init'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.fronpage_url))

    def test_init_reset_password_with_email(self):
        # Test that init reset password works correct.
        data = {'username_or_email': 'john@example.com'}
        response = self.client.post(self.reset_password_init, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.fronpage_url))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         u'Reset your OER Commons password')

        response = self.client.get(self.fronpage_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'We have sent a link to reset your password to %s.' % data['username_or_email'])

    def test_init_reset_password_with_username(self):
        # Test that init reset password works correct.
        data = {'username_or_email': 'testuser'}
        response = self.client.post(self.reset_password_init, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.fronpage_url))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         u'Reset your OER Commons password')

        response = self.client.get(self.fronpage_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'We have sent a link to reset your password to your email.')



class ResetPasswordViewTest(TestCase, TestDataGenerator):

    fixtures = ['users_test_data.json']

    def setUp(self):
        user = User.objects.get(username='testuser')
        self.confirmation = ResetPasswordConfirmation.objects.create(user=user)
        self.login_url = reverse('users:login')
        self.reset_password_url = reverse('users:reset_password',
                                          args=[self.confirmation.key])

    def test_key_is_none(self):
        # Test that key is None.
        reset_password_url = reverse('users:reset_password', args=[None])
        print reset_password_url
        response = self.client.get(reset_password_url)
        self.assertEqual(response.status_code, 404)

    def test_reset_password_template(self):
        # Test reset password view was rendered with correct template.
        response = self.client.get(self.reset_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/reset-password.html')

    def test_reset_password(self):
        # Test that reset password works correct.
        password = self.get_test_password()
        data = {
            'password': password,
            'confirm_password': password
        }
        response = self.client.post(self.reset_password_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.login_url))

        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Your password was changed successfully. You can use it to log in now.')

    def test_form_invalid(self):
        # Test that if form is invalid error message was shown.
        data = {
            'password': self.get_test_password(),
            'confirm_password': self.get_test_password()
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Please correct the indicated errors.')


