from annoying.decorators import JsonResponse
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, \
    logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from utils.shortcuts import redirect_to_next_url
import re



class LoginForm(AuthenticationForm):

    username = forms.CharField(label=u"Your email or username:",
                             widget=forms.TextInput(attrs={"size": 25,
                                                           "class": "text"}))

    password = forms.CharField(label=u"Password:",
                             widget=forms.PasswordInput(attrs={"size": 25,
                                                           "class": "text"}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct email (username) and password. Note that password is cAsE-sEnsItiVe."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive. Make sure that you've followed the instructions in registration confirmation email."))

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))

        return self.cleaned_data


def login(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("frontpage"))

    page_title = u"Log in"
    breadcrumbs = [{"url": reverse("users:login"), "title": page_title}]

    redirect_to = request.REQUEST.get(settings.REDIRECT_FIELD_NAME, '')

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if request.is_ajax():
            if form.is_valid():
                auth_login(request, form.get_user())
                return JsonResponse(dict(status="success"))
            else:
                errors = {}
                for field_name, errors_list in form.errors.items():
                    errors[field_name] = errors_list[0]
                return JsonResponse(dict(status="error", errors=errors))
                
        else:
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

                return HttpResponseRedirect(redirect_to)
            else:
                messages.error(request, u"Invalid email and/or password.")

    else:
        form = LoginForm(request)

    return direct_to_template(request, "users/login.html", locals())


def render_login_form(request):
    form = LoginForm()
    return direct_to_template(request, "users/login-form.html", locals())
 

def logout(request):
    auth_logout(request)
    return redirect_to_next_url(request)

