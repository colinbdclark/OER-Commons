from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
import re


def redirect_to_next_url(request, default=None):

    redirect_to = request.REQUEST.get(settings.REDIRECT_FIELD_NAME, '')
    if default is None:
        default = reverse("frontpage")

    # Light security check -- make sure redirect_to isn't garbage.
    if not redirect_to or ' ' in redirect_to:
        redirect_to = default

    # Heavier security check -- redirects to http://example.com should 
    # not be allowed, but things like /view/?param=http://example.com 
    # should be allowed. This regex checks if there is a '//' *before* a
    # question mark.
    elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
        redirect_to = default

    return HttpResponseRedirect(redirect_to)
