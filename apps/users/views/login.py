from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from utils.shortcuts import redirect_to_next_url
import re


class LoginForm(AuthenticationForm):

    username = forms.CharField(label=u"User name:",
                             widget=forms.TextInput(attrs={"size": 25,
                                                           "class": "text"}))

    password = forms.CharField(label=u"Password:",
                             widget=forms.PasswordInput(attrs={"size": 25,
                                                           "class": "text"}))


def login(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("frontpage"))

    page_title = u"Log in"
    breadcrumbs = [{"url": reverse("users:login"), "title": page_title}]

    redirect_to = request.REQUEST.get(settings.REDIRECT_FIELD_NAME, '')

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = reverse("frontpage")

            # Heavier security check -- redirects to http://example.com should 
            # not be allowed, but things like /view/?param=http://example.com 
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                redirect_to = reverse("frontpage")

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            messages.success(request, u"You are logged in now.")

            return HttpResponseRedirect(redirect_to)
        else:
            messages.error(request, u"Invalid user name and/or password.")

    else:
        form = LoginForm(request)

    return direct_to_template(request, "users/login.html", locals())


def logout(request):
    auth_logout(request)
    messages.success(request, u"You are now logged out.")
    return redirect_to_next_url(request)

