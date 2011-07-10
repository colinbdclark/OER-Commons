# -*- coding: utf-8 -*-

import time
import urllib
import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.conf import settings

from users.views.registration import RegistrationForm, ConfirmationForm
from users.models import RegistrationConfirmation, gen_confirmation_key


class RegistrationFormTest(TestCase):

    def test_success(self):
        # Test that form is valid with correct data.
        data = {
            'email': 'john@example.com',
            'password': 'password',
            }
        form = RegistrationForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        # Test that form is invalid with incorrect email.
        data = {
            'email': 'john#example.com',
            'password': 'password',
            }
        form = RegistrationForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['email'].errors,
                         [u'Enter a valid e-mail address.'])

    def test_invalid_password(self):
        # Test that form is invalid if password is too short.
        data = {
            'email': 'john@example.com',
            'password': '123',
            }

        form = RegistrationForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['password'].errors,
                         [u'Ensure this value has at least 5 characters (it has 3).'])

class ConfirmationFormTest(TestCase):

    fixtures = ['users_test_data.json']

    def setUp(self):
        user = User.objects.get(username='testuser')
        self.code = gen_confirmation_key()
        self.unconfirmed_registration = RegistrationConfirmation.objects.create(
            user=user,
            key=self.code,
            confirmed=False,
        )

    def test_invalid_confirmation_code(self):
        # Test that recived confimation code is invalid or doesn't exist.
        data = {
            'code': u'mEZkMun8waDNf55g5fJX'
        }
        form = ConfirmationForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form['code'].errors,
                         [u'Invalid confirmation code.'])

    def test_account_confirmed_already(self):
        # Test that account is already confirmed.
        confirmed_registration = self.unconfirmed_registration
        confirmed_registration.confirmed = True
        confirmed_registration.save()

        data = {
            'code': self.code
        }
        form = ConfirmationForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form['code'].errors,
            [u'The account with this confirmation code is confirmed already.']
        )


class RegistrationViewTest(TestCase):

    fixtures = ['users_test_data.json']

    def setUp(self):
        self.honeypot_value = settings.HONEYPOT_VALUE()
        self.honeypot_field = settings.HONEYPOT_FIELD_NAME

        self.data = {
            'email': 'john@example.com',
            'password': 'password',
            self.honeypot_field: self.honeypot_value,
        }

        self.login = reverse('users:login')
        self.frontpage = reverse('frontpage')
        self.registration = reverse('users:registration')
        self.resend_confirmation = reverse('users:registration_resend')

    def test_honeypot_decorator(self):
        # Test checking HONEYPOT_VALUE.
        incorrect_honeypot_value = int(time.time() - 60 * 60 * 2)

        data = self.data
        data[self.honeypot_field] = incorrect_honeypot_value

        response = self.client.post(self.registration, data)
        self.assertEqual(response.status_code, 400)

    def test_user_is_authenticated(self):
        #Test than view redirect to front page if user is already authenticated
        login_data = {
            'username': 'john@example.com',
            'password': 'password',
        }
        response = self.client.post(self.login, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.frontpage))

        response = self.client.post(self.registration, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.frontpage))

    def test_user_already_exists(self):
        # Test that user is already exist.
        reset_password_url = reverse('users:reset_password_init')
        email = self.data['email']
        message = u'User with email <em>%(email)s</em> is registered already. If you forgot your password you can <a href="%(url)s">click here</a> to reset it.'
        message = message % dict(email=email, url=reset_password_url)

        response = self.client.post(self.registration, self.data)
        self.assertContains(response, message)

    def test_account_confirm_required(self):
        data = self.data
        data['email'] = 'joanna@example.com'

        self.assertTrue(RegistrationConfirmation.objects.all().exists())

        email = self.data['email']
        message = u'A registration request for the user account with email <em>%(email)s</em> needs to be confirmed. <a href="%(url)s?email=%(email)s">Click here</a> to re-send the confirmation email.'
        message = message % dict(email=email, url=self.resend_confirmation)

        response = self.client.post(self.registration, data)
        self.assertContains(response, message)

    def test_form_invalid(self):
        # Test that form is invalid
        data = self.data
        data['email'] = 'john#example.com'

        response = self.client.post(self.registration, data)
        self.assertContains(response, u'Please correct the indicated errors.')

    def test_request_get(self):
        # Test that get request work correctly and render with correct template
        response = self.client.get(self.registration)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/registration.html')

    def test_success_registration(self):
        # Test that registration process completed successfully.
        welcome = reverse('users:welcome')
        data = self.data
        data['email'] = 'test@example.com'

        response = self.client.post(self.registration, data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         u'Confirm your registration at OER Commons')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(welcome))

        # Test that email contents correct confirmation link.
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            self.fail('User does not exist')
        else:
            try:
                confirmation = RegistrationConfirmation.objects.get(user=user)
            except RegistrationConfirmation.DoesNotExist:
                self.fail('RegistrationConfirmation does not exist')
            else:
                key = confirmation.key
                reversed_url = reverse("users:registration_confirm")
                confirmation_link = '%s?code=%s' % (reversed_url, key)
                self.assertTrue(confirmation_link in mail.outbox[0].body)

        # Test that warning message shows when user account isn't confirmed.
        response = self.client.get(self.frontpage)
        message = 'You haven\'t confirmed your email address yet. Please follow the instructions in confirmation email that we have sent to you.'
        self.assertContains(response, message)

        # Test that number of days is correctly.
        now = datetime.datetime.now()
        days_to_delete = (now + datetime.timedelta(days=30) - confirmation.timestamp).days
        message_with_days = 'in %s days' % days_to_delete
        self.assertContains(response, message_with_days)

        # Test that link to resend email confirmation exists in warning message.
        quoted_email = urllib.quote(data['email'])
        resend_link = '%s?email=%s' % (self.resend_confirmation, quoted_email)
        self.assertContains(response, resend_link)


class ResendViewTest(TestCase):

    fixtures = ['users_test_data.json']

    def setUp(self):
        self.resend_confirmation = reverse('users:registration_resend')
        self.login = reverse('users:login')
        self.frontpage = reverse('frontpage')

        email = 'joanna@example.com'
        quoted_email = urllib.quote(email)
        self.resend_link = '%s?email=%s' % (self.resend_confirmation, quoted_email)

    def test_404(self):
        response = self.client.get(self.resend_confirmation)
        self.assertEqual(response.status_code, 404)

    def test_resend_confirmation_with_email(self):
        # Test confirmation resend with email.
        self.client.get(self.resend_link)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         u'Confirm your registration at OER Commons')

    def test_resend_confirmation_with_username(self):
        # Test confirmation resend with username.
        try:
            user = User.objects.get(username='testuser2')
        except User.DoesNotExist:
            self.fail('User does not exist')

        resend_link_with_username = '%s?username=%s' % (self.resend_confirmation, user.username)

        self.client.get(resend_link_with_username)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         u'Confirm your registration at OER Commons')

    def test_user_is_authenticated_and_confirmed(self):
        # Test that view redirect if user is authenticated and confirmed already
        login_data = {
            'username': 'john@example.com',
            'password': 'password',
        }
        response = self.client.post(self.login, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.frontpage))

        response = self.client.get(self.resend_link)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.frontpage))
        # self.assertRedirects(response, self.frontpage, status_code=302, target_status_code=200)


class ConfirmViewTest(TestCase):

    fixtures = ['users_test_data.json']

    def setUp(self):
        self.data = {
            'email': 'joanna@example.com',
            'password': 'password'
        }
        self.frontpage = reverse('frontpage')
        self.registration_confirm = reverse("users:registration_confirm")
        self.user = User.objects.get(email=self.data['email'])
        self.confirmation = RegistrationConfirmation.objects.get(user=self.user)

    def test_request_get(self):
        # Test that get request work correctly and render with correct template
        response = self.client.get(self.registration_confirm)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/registration-confirm.html')

    def test_form_invalid(self):
        # Test that form is invalid
        code = '1234567890'
        response = self.client.post(self.registration_confirm, {'code': code})
        self.assertContains(response, u'Please correct the indicated errors.')

    def test_confirmation(self):
        # Test that confirmation link and view work correctly.
        code = self.confirmation.key
        response = self.client.post(self.registration_confirm, {'code': code})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(self.frontpage))

    def test_days_to_delete(self):
        confirmation = self.confirmation
        incorrect_date = datetime.datetime.now() - datetime.timedelta(days=30)
        confirmation.timestamp = incorrect_date
        confirmation.save()

        self.assertEqual(RegistrationConfirmation.objects.all().count(), 2)

        call_command('delete_old_unconfirmed_accounts', interactive=False)

        self.assertEqual(RegistrationConfirmation.objects.all().count(), 1)


class WelcomeViewTest(TestCase):

    def test_welcome(self):
        response = self.client.get(reverse('users:welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/welcome.html')
