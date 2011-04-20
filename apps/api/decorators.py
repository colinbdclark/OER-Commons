from annoying.decorators import JsonResponse
from api import APIError
import sys


def api_method(func):

    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError:
            return JsonResponse(dict(error=unicode(sys.exc_info()[1])))

    return decorated
