# -*- coding: utf-8 -*-

from django.test import TestCase

from users.backend import (BCRYPT_PREFIX, BcryptBackend, check_password,
    encrypt_password)
from users.tests.utils import TestDataGenerator


class EncryptPasswordTest(TestCase, TestDataGenerator):

    fixtures = ['users_test_data.json']

    def test_encrypt_password(self):
        # Test encypt password function.
        password = self.get_test_password()
        result = encrypt_password(password)
        self.assertTrue(result.startswith(BCRYPT_PREFIX))

    def test_encrypt_unicode_password(self):
        # Test encrypt unicode password condition.
        password = unicode(self.get_test_password())
        result = encrypt_password(password)
        self.assertTrue(result.startswith(BCRYPT_PREFIX))


class CheckPasswordTest(TestCase):

    fixtures = ['users_test_data.json']

    def test_check_none_bcrypt_password(self):
        # Test that encrypted password is none bcrypt.
        encrypted_password = 'sha1$6dbae$dd62c29a3c7a92e88918f92a6200ea18450d9f19'
        password = 'password'
        result = check_password(encrypted_password, password)
        self.assertFalse(result)

    def test_check_unicode_password(self):
        # Test unicode encrypted password.
        encrypted_password = 'bcrypt$$2a$12$5V5ZGlf.IH2O1qDvEg/2ceuFbLWB2UBhqQok4owqYU5IH3izwpswe'
        password = unicode('password')
        result = check_password(encrypted_password, password)
        self.assertTrue(result)

    def test_check_password(self):
        # Test unicode encrypted password.
        encrypted_password = 'bcrypt$$2a$12$5V5ZGlf.IH2O1qDvEg/2ceuFbLWB2UBhqQok4owqYU5IH3izwpswe'
        password = 'password'
        result = check_password(encrypted_password, password)
        self.assertTrue(result)


class BcryptBackendTest(TestCase):

    fixtures = ['users_test_data.json']

    def setUp(self):
        self.backend = BcryptBackend()

    def test_authenticate_without_username(self):
        # Test that method interrupts if username is None.
        user = self.backend.authenticate(password='password')
        self.assertFalse(user)

    def test_authenticate_without_password(self):
        # Test that method interrupts if password is None.
        user = self.backend.authenticate(username='testuser')
        self.assertFalse(user)

    def test_unsuccessful_authenticate(self):
        # Test that method returns None if authenticate is unsuccessful.
        data = {
            'username': 'wrong_user',
            'password': 'wrong_password'
        }
        user = self.backend.authenticate(**data)
        self.assertFalse(user)

    def test_successful_authenticate(self):
        # Test authenticate method of backend with bcrypt password.
        data = {
            'username': 'testuser',
            'password': 'password'
        }
        user = self.backend.authenticate(**data)
        self.assertEqual(user.username, data['username'])

    def test_successful_authenticate_not_bcrypt(self):
        # Test authenticate method of backend with none bcrypt password.
        data = {
            'username': 'testuser3',
            'password': 'password'
        }
        user = self.backend.authenticate(**data)
        self.assertEqual(user.username, data['username'])

    def test_get_existing_user(self):
        # Test get existing user.
        user_id = 1
        user = self.backend.get_user(user_id)
        self.assertEqual(user.username, 'testuser')

    def test_get_none_existing_user(self):
        # Test get none existing user.
        user_id = 99
        user = self.backend.get_user(user_id)
        self.assertFalse(user)
