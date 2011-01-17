from api import APIError
from api.shortcuts import api_response
import sys


def api_method(func):

    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError:
            return api_response(dict(error=unicode(sys.exc_info()[1])))

    return decorated
