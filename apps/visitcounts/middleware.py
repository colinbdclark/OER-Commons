from visitcounts.models import UniqueVisitor


COOKIE_NAME = "uniquevisitor"
ANONYMOUS_COOKIE_VALUE = "0"
AUTHENTICATED_COOKIE_VALUE = "1"


class UniqueVisitorMiddleware(object):
    
    def process_response(self, request, response):
        is_authenticated = request.user.is_authenticated()
        cookie_value = is_authenticated and AUTHENTICATED_COOKIE_VALUE or ANONYMOUS_COOKIE_VALUE
        if request.COOKIES.get(COOKIE_NAME, None) != cookie_value:
            UniqueVisitor.objects.create(is_authenticated=is_authenticated)
            response.set_cookie(COOKIE_NAME, cookie_value)
        return response
    