from django import forms
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Max
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from honeypot.decorators import check_honeypot
from newsletter.tasks import subscribe
from users.backend import encrypt_password, BcryptBackend
from users.models import RegistrationConfirmation, Profile


class RegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=30, label=u"Your first name:",
                           widget=forms.TextInput(attrs={"size": 50,
                                                         "class": "text"}))

    last_name = forms.CharField(max_length=30, label=u"Your last first name:",
                           widget=forms.TextInput(attrs={"size": 50,
                                                         "class": "text"}))

    email = forms.EmailField(label=u"Email:", max_length=75,
                             help_text=u"Enter your email address. This is "
                             "used to confirm your registration, so please "
                             "use a valid email address. We respect your "
                             "privacy, and will not share your information "
                             "with third parties.",
                             widget=forms.TextInput(attrs={"size": 40,
                                                           "class": "text"}))

    password = forms.CharField(min_length=5, label=u"Password:",
                               help_text=u"Minimum of five characters, "
                                          "case sensitive.",
                               widget=forms.PasswordInput(attrs={"size": 15,
                                                         "class": "text",
                                                      "autocomplete": "off"}))

    confirm_password = forms.CharField(min_length=5,
                            label=u"Confirm password:",
                            help_text=u"Re-enter your password.",
                            widget=forms.PasswordInput(attrs={"size": 15,
                                                         "class": "text",
                                                     "autocomplete": "off"}))

    newsletter = forms.BooleanField(label=u"Subscribe to the OER Commons Monthly Newsletter",
                                    widget=forms.CheckboxInput(),
                                    required=False,
                                    initial=True)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            email = email.lower()
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password", "")
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise forms.ValidationError(u"The two passwords do not match.")
        return confirm_password


class ConfirmationForm(forms.Form):

    code = forms.CharField(label=u"Confirmation code:",
                           widget=forms.TextInput(attrs={"size": 30,
                                                         "class": "text"}))

    def clean_code(self):
        code = self.cleaned_data["code"]
        try:
            confirmation = RegistrationConfirmation.objects.get(key=code)
            if confirmation.confirmed:
                raise forms.ValidationError(u"The account with this confirmation code is confirmed already.")
        except RegistrationConfirmation.DoesNotExist:
            raise forms.ValidationError(u"Invalid confirmation code.")
        return code


@check_honeypot
def registration(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("frontpage"))

    page_title = u"Registration"
    breadcrumbs = [{"url": reverse("users:registration"), "title": page_title}]

    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data["email"]
            username = "user%i" % (User.objects.aggregate(Max("id"))["id__max"] + 1)
            email_taken = False
            email_pending = False
            if User.objects.filter(email=email).exists():
                email_taken = True
                user = User.objects.get(email=email)
                if RegistrationConfirmation.objects.filter(user=user, confirmed=False).count():
                    email_pending = True

            if email_pending:
                resend_confirmation_url = reverse("users:registration_resend")
                message = u"A registration request for the user account with email <em>%(email)s</em> needs to be confirmed. <a href=\"%(url)s?email=%(email)s\">Click here</a> to re-send the confirmation email."
                message = message % dict(email=email,
                                         url=resend_confirmation_url)
                messages.warning(request, message)
                return direct_to_template(request, "users/registration.html", locals())

            elif email_taken:
                reset_password_url = reverse("users:reset_password_init")
                message = u"User with email <em>%(email)s</em> is registered already. If you forgot your password you can <a href=\"%(url)s\">click here</a> to reset it."
                message = message % dict(email=email,
                                         url=reset_password_url)
                messages.warning(request, message)
                return direct_to_template(request, "users/registration.html", locals())

            else:
                first_name = data["first_name"]
                last_name = data["last_name"]
                password = encrypt_password(data["password"])
                user = User(username=username, first_name=first_name,
                            last_name=last_name, email=email,
                            password=password, is_active=False)
                user.save()
                profile = Profile(user=user)
                profile.save()
                confirmation = RegistrationConfirmation(user=user,
                                                        confirmed=False)
                confirmation.save()
                confirmation.send_confirmation()
                
                if data["newsletter"]:
                    kwargs = {}
                    if first_name:
                        kwargs["first_name"] = first_name
                    if last_name:
                        kwargs["last_name"] = last_name
                    subscribe.delay(email, **kwargs)

                messages.success(request, u"Confirmation email was sent to you.")
                return HttpResponseRedirect(reverse("frontpage"))

        else:
            messages.error(request, u"Please correct the indicated errors.")

    return direct_to_template(request, "users/registration.html", locals())


def confirm(request):

    page_title = u"Confirm Registration"
    form = ConfirmationForm()

    if "code" in request.REQUEST:
        form = ConfirmationForm(request.REQUEST)
        if form.is_valid():
            confirmation = RegistrationConfirmation.objects.get(key=form.cleaned_data["code"])
            confirmation.confirm()
            user = confirmation.user
            backend = BcryptBackend()
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            auth_login(request, user)
            messages.success(request, u"Thank you for registration. Your account was created.")
            return HttpResponseRedirect(reverse("users:welcome"))
        else:
            messages.error(request, u"Please correct the indicated errors.")

    return direct_to_template(request, "users/registration-confirm.html",
                              locals())


def welcome(request):
    
    page_title = u"Welcome to OER Commons"
    
    return direct_to_template(request, "users/welcome.html", locals())


def resend(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("frontpage"))

    username = request.REQUEST.get("username", u"").strip()
    email = request.REQUEST.get("email", u"").strip()

    if not email and not email:
        raise Http404()

    kwargs = {}
    if email:
        kwargs["email"] = email
    if username:
        kwargs["username"] = username

    user = get_object_or_404(User, **kwargs)
    confirmation = get_object_or_404(RegistrationConfirmation, user=user)
    if confirmation.confirmed:
        messages.success(request, u"This user account is confirmed already.")
        return HttpResponseRedirect(reverse("users:login"))
    else:
        confirmation.send_confirmation()
        messages.success(request, u"Confirmation email was sent to you.")
        return HttpResponseRedirect(reverse("frontpage"))
