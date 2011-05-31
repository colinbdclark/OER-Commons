from users.models import RegistrationConfirmation


class LazyConfirmedPropery(object):
    
    def __init__(self, user):
        self.user = user
        self.confirmed = None

    def __nonzero__(self):
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