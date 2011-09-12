# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse


class LoginViewTest(TestCase):

    fixtures = ['users_data.json']

    def test_login(self):
        # Test log in with new user account
        login = reverse('users:login')
        frontpage = reverse('frontpage')
        login_data = {
            'username': 'john@example.com',
            'password': 'password',
        }
        response = self.client.post(login, login_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(frontpage))

    def test_logout(self):
        # Test logout
        frontpage = reverse('frontpage')
        logout = reverse('users:logout')

        response = self.client.get(logout)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(frontpage))

