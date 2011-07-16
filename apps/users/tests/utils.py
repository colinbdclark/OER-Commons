# -*- coding: utf-8 -*-

import random
import string

from django.conf import settings

import faker


class TestDataGenerator(object):

    PASSWORD_LENGTH = 8

    def get_test_userdata(self):
        # Returns fake email and password
        password = ''.join(random.choice(string.letters + string.digits) for x in xrange(self.PASSWORD_LENGTH))
        return {
            'email': faker.internet.email(),
            'password': password
        }

    def get_honeypot(self):
        # Returns honeypot value
        return settings.HONEYPOT_VALUE()
