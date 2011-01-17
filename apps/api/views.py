from django.http import HttpResponse
from oauth_provider.decorators import oauth_required


@oauth_required
def dummy(request):
    return HttpResponse(request.user, content_type="text/plain")
