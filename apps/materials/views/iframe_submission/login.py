from annoying.decorators import ajax_request
from django.contrib.auth import login as auth_login
from django.http import Http404
from users.views.login import LoginForm


@ajax_request
def login(request):

    if request.user.is_authenticated():
        return dict(status="success")

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            return dict(status="success")
        else:
            errors = {}
            for field, errors_list in form.errors.items():
                errors[field] = errors_list[0]  
            return dict(status="error", errors=errors)

    else:
        raise Http404()
