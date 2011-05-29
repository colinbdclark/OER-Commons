from preferences.models import PREFERENCE_FIELDS, Preferences
import json


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
                    model_preferences = Preferences.objects.get(user=self.user)
                except Preferences.DoesNotExist:
                    model_preferences = None
                self._model_preferences = model_preferences
            if self._model_preferences is not None:
                value = getattr(self._model_preferences, name, None)

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