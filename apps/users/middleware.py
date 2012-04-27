from users.models import PREFERENCE_FIELDS, Profile
import json


class LazyConfirmedPropery(object):

    def __init__(self, user):
        self.user = user
        self.confirmed = None

    def __nonzero__(self):
        from users.models import RegistrationConfirmation
        if self.confirmed is None:
            self.confirmed = True
            try:
                self.confirmed = RegistrationConfirmation.objects.get(user=self.user).confirmed
            except RegistrationConfirmation.DoesNotExist:
                pass
        return self.confirmed

    def __repr__(self):
        return str(self.__nonzero__())


class ConfirmationMiddleware(object):

    def process_request(self, request):
        user = request.user
        if request.user.is_anonymous():
            return None

        user.is_confirmed = LazyConfirmedPropery(user)

        return None


class LazyPreferences(object):

    def __init__(self, request):
        self.request = request
        user = getattr(request, "user", None)
        if user and user.is_anonymous():
            user = None
        self.user = user

    def __getattr__(self, name):
        cached_name = "_%s" % name
        try:
            return super(LazyPreferences, self).__getattr__(cached_name)
        except AttributeError:
            pass

        if name not in PREFERENCE_FIELDS:
            raise AttributeError()

        value = None

        cookie_name, default_value = PREFERENCE_FIELDS[name]

        if self.user:
            if not hasattr(self, "_model_preferences"):
                try:
                    model_preferences = Profile.objects.values(*PREFERENCE_FIELDS).get(user=self.user)
                except Profile.DoesNotExist:
                    model_preferences = None
                self._model_preferences = model_preferences
            if self._model_preferences is not None:
                value = self._model_preferences.get(name)

        if value is None:
            cookie_value = self.request.COOKIES.get(cookie_name, None)
            if cookie_value:
                try:
                    value = json.loads(cookie_value)
                except ValueError:
                    pass

        if value is None:
            value = default_value

        setattr(self, cached_name, value)
        return value


class PreferencesMiddleware(object):

    def process_request(self, request):
        request.preferences = LazyPreferences(request)
        return None