# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.conf import settings

import faker


class TestDataGenerator(object):

    PASSWORD_LENGTH = 8

    def get_test_password(self, length=None):
        # Returns random password.
        if not length:
            length = self.PASSWORD_LENGTH
        return User.objects.make_random_password(length=length)

    def get_test_userdata(self):
        # Returns fake email and password.
        return {
            'email': faker.internet.email(),
            'password': self.get_test_password(self.PASSWORD_LENGTH)
        }

    def get_honeypot(self):
        # Returns honeypot value.
        return settings.HONEYPOT_VALUE()
