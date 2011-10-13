import re


class BrowserDetectMiddleware(object):

    IE_RE = re.compile(r"MSIE [0-9]+[\.0-9]*")

    def process_request(self, request):
        request.is_ie = False
        ua = request.META.get("HTTP_USER_AGENT", "")
        print "!!!!", ua, self.IE_RE.match(ua)
        if self.IE_RE.search(ua):
            request.is_ie = True
        return None
