from django.views.generic.simple import direct_to_template


def frontpage(request):
    return direct_to_template(request, "frontpage.html", locals())
