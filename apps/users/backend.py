from django.contrib.auth.models import User
import bcrypt
from django.contrib.auth.backends import ModelBackend


BCRYPT_PREFIX = "bcrypt$"


def encrypt_password(password):
    return BCRYPT_PREFIX + bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(encrypted_password, password):
    if not encrypted_password.startswith(BCRYPT_PREFIX):
        return False
    encrypted_password = encrypted_password[len(BCRYPT_PREFIX):]
    salt = encrypted_password[:29]
    return bcrypt.hashpw(password, salt) == encrypted_password



class BcryptBackend(ModelBackend):

    def authenticate(self, username=None, password=None):

        if username is None or password is None:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if not user.password.startswith(BCRYPT_PREFIX):
            return super(BcryptBackend, self).authenticate(username, password)

        if check_password(user.password, password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
