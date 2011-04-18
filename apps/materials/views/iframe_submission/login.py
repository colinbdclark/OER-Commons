from django.contrib.auth import login as auth_login
from django.http import HttpResponse, Http404
from users.views.login import LoginForm
import cjson


def login(request):

    if request.user.is_authenticated():
        return HttpResponse(cjson.encode(dict(status="success")),
                            content_type="application/json")

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            return HttpResponse(cjson.encode(dict(status="success")),
                                content_type="application/json")
        else:
            errors = {}
            for field, errors_list in form.errors.items():
                errors[field] = errors_list[0]  
            return HttpResponse(cjson.encode(dict(status="error",
                                                  errors=errors)),
                                content_type="application/json")

    else:
        raise Http404()
