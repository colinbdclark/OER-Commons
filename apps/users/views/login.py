from annoying.decorators import JsonResponse
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, \
    logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
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

        self.check_for_test_cookie()
        return self.cleaned_data


class Login(TemplateView):

    popup = False

    def dispatch(self, request, *args, **kwargs):
        return super(Login, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        if not self.popup and request.user.is_authenticated():
            return redirect("frontpage")
        self.form = LoginForm()
        return super(Login, self).get(request, **kwargs)

    def post(self, request, **kwargs):
        self.form = LoginForm(data=request.POST)
        redirect_to = request.REQUEST.get(settings.REDIRECT_FIELD_NAME, '')
        if request.is_ajax():
            if self.form.is_valid():
                user = self.form.get_user()
                auth_login(request, user)
                return JsonResponse(dict(status="success",
                                         user_name=user.get_full_name() or user.email or unicode(user)))
            else:
                errors = {}
                for field_name, errors_list in self.form.errors.items():
                    errors[field_name] = errors_list[0]
                return JsonResponse(dict(status="error", errors=errors))

        if self.form.is_valid():
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
            auth_login(request, self.form.get_user())

            if self.popup:
                return self.get(request, **kwargs)

            return redirect(redirect_to)

        else:
            messages.error(request, u"Invalid email and/or password.")

        return self.get(request, **kwargs)

    def get_template_names(self):
        if self.popup:
            return ["users/login-popup.html"]
        return ["users/login.html"]

    def get_context_data(self, **kwargs):
        data = super(Login, self).get_context_data(**kwargs)
        data["form"] = self.form
        data["page_title"] = u"Log in"
        data["breadcrumbs"] = [{"url": reverse("users:login"), "title": data["page_title"]}]
        return data


def render_login_form(request):
    return render(request, "users/login-form.html", dict(form=LoginForm(),
                                                         in_dialog=True))


def logout(request):
    auth_logout(request)
    return redirect_to_next_url(request)

