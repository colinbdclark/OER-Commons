from django.views.generic.simple import direct_to_template


def oai_error(request, verb, code, message):
    return direct_to_template(request,
                              dict(verb=verb, code=code, message=message),
                              mimetype="text/xml")
