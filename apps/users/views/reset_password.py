from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.generic.simple import direct_to_template
from django.contrib.auth.models import User
from users.models import ResetPasswordConfirmation
from django.shortcuts import get_object_or_404
from django.contrib import messages


class InitResetPasswordForm(forms.Form):

    email = forms.EmailField(label=u"Your email:",
                             help_text=u"Please enter the email address you "
                             "used to create your OER Commons account, and we "
                             "will send you a link to reset your password.",
                             widget=forms.TextInput(attrs={"size": 40,
                                                           "class": "text"}))


    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(u"User account with this email is not registered.")
        return email


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
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)
            confirmation = ResetPasswordConfirmation(user=user)
            confirmation.save()
            confirmation.send_confirmation()
            messages.success(request, u"We have sent a link to reset your password to %s." % email)
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

