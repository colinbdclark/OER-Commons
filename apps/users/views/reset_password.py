from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import email_re
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from users.models import ResetPasswordConfirmation


class InitResetPasswordForm(forms.Form):

    username_or_email = forms.CharField(label=u"Your username or email:",
                             widget=forms.TextInput(attrs={"size": 40,
                                                           "class": "text"}))


    def clean_username_or_email(self):
        username_or_email = self.cleaned_data["username_or_email"].strip()
        if email_re.match(username_or_email):
            try:
                self.user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise forms.ValidationError(u"""User account with this email is not registered. <a href="#">Register now.</a>""")
        else:
            try:
                self.user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                raise forms.ValidationError(u"""User account with this username is not registered. <a href="#">Register now.</a>""")
        return username_or_email


class ResetPasswordForm(forms.Form):

    password = forms.CharField(min_length=5, label=u"New password:",
                               help_text=u"Minimum of five characters, "
                                          "case sensitive.",
                               widget=forms.PasswordInput(attrs={"size": 15,
                                                         "class": "text",
                                                      "autocomplete": "off"}))

    confirm_password = forms.CharField(min_length=5,
                            label=u"Confirm password:",
                            help_text=u"Re-enter your new password.",
                            widget=forms.PasswordInput(attrs={"size": 15,
                                                         "class": "text",
                                                     "autocomplete": "off"}))

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password", "")
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise forms.ValidationError(u"The two passwords do not match.")
        return confirm_password


def init(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("frontpage"))

    page_title = u"Password Assistance"
    breadcrumbs = [{"url": reverse("users:reset_password_init"), "title": page_title}]

    form = InitResetPasswordForm()
    if request.method == "POST":
        form = InitResetPasswordForm(request.POST)
        if form.is_valid():
            user = form.user
            confirmation = ResetPasswordConfirmation(user=user)
            confirmation.save()
            confirmation.send_confirmation()
            if email_re.match(form.cleaned_data["username_or_email"]):
                messages.success(request, u"We have sent a link to reset your password to %s." % user.email)
            else:
                messages.success(request, u"We have sent a link to reset your password to your email.")
            return HttpResponseRedirect(reverse("frontpage"))

    return direct_to_template(request, "users/reset-password-init.html", locals())


def reset_password(request, key=None):

    if key is None:
        raise Http404()

    page_title = u"Reset password"
    breadcrumbs = [{"url": reverse("users:reset_password_init"), "title": page_title}]

    confirmation = get_object_or_404(ResetPasswordConfirmation, key=key, confirmed=False)
    form = ResetPasswordForm()
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            confirmation.confirm(form.cleaned_data["password"])
            messages.success(request, u"Your password was changed successfully. You can use it to log in now.")
            return HttpResponseRedirect(reverse("users:login"))
        else:
            messages.error(request, u"Please correct the indicated errors.")

    return direct_to_template(request, "users/reset-password.html", locals())

