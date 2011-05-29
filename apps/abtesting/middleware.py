import random


AB_TESTING_COOKIE_NAME = "_ab"
AB_TESTING_COOKIE_VALUES = ("a", "b")


class ABTestingMiddleware(object):
    
    def process_request(self, request):
        value = request.GET.get(AB_TESTING_COOKIE_NAME, None)
        if value not in AB_TESTING_COOKIE_VALUES:
            value = request.COOKIES.get(AB_TESTING_COOKIE_NAME, None)
        if value not in AB_TESTING_COOKIE_VALUES:
            value = random.choice(AB_TESTING_COOKIE_VALUES)
        request.abtesting = value
        return None
    
    def process_response(self, request, response):
        if AB_TESTING_COOKIE_NAME not in request.COOKIES and \
            getattr(request, "abtesting", None) in AB_TESTING_COOKIE_VALUES:
            max_age = 3600 * 24 * 365 * 2 # Two years
            response.set_cookie(AB_TESTING_COOKIE_NAME, request.abtesting,
                                max_age=max_age)
        return response