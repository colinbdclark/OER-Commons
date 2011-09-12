# -*- coding: utf-8 -*-

import random
import string

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

    def get_str_number(self, length):
        # Returns random string with numbers and and a given length.
        return ''.join(random.choice(string.digits) for i in xrange(length))

    def get_test_userdata(self):
        # Returns fake email and password.
        return {
            'email': faker.internet.email(),
            'password': self.get_test_password(self.PASSWORD_LENGTH)
        }

    def get_honeypot(self):
        # Returns honeypot value.
        return settings.HONEYPOT_VALUE()

    def get_full_name(self):
        # Return dict with first and last names.
        return {
            'first_name': faker.name.first_name(),
            'last_name': faker.name.last_name()
        }
