from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
import bcrypt


BCRYPT_PREFIX = "bcrypt$"


def encrypt_password(password):
    if isinstance(password, unicode):
        password = password.encode("utf-8")
    return BCRYPT_PREFIX + bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(encrypted_password, password):
    if not encrypted_password.startswith(BCRYPT_PREFIX):
        return False
    encrypted_password = encrypted_password[len(BCRYPT_PREFIX):]
    salt = encrypted_password[:29]
    if isinstance(password, unicode):
        password = password.encode("utf-8")
    return bcrypt.hashpw(password, salt) == encrypted_password



class BcryptBackend(ModelBackend):

    def authenticate(self, username=None, password=None):

        if username is None or password is None:
            return None

        for user in User.objects.filter(Q(username=username) | Q(email__iexact=username)):
            
            if not user.password.startswith(BCRYPT_PREFIX):
                result = super(BcryptBackend, self).authenticate(user.username, password)
                if result:
                    return result
    
            elif check_password(user.password, password):
                return user
    
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
