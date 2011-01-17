from django.http import HttpResponse
import cjson


def api_response(data):
    return HttpResponse(cjson.encode(data), content_type="application/json")
