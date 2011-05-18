from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from honeypot.decorators import check_honeypot
from users.backend import encrypt_password, BcryptBackend
from users.models import MEMBER_ROLES, RegistrationConfirmation, Profile
import mailchimp


class RegistrationForm(forms.Form):

    name = forms.CharField(max_length=61, label=u"Your name:",
                           help_text=u"Enter your full name.",
                           widget=forms.TextInput(attrs={"size": 50,
                                                         "class": "text"}))

    username = forms.RegexField(label="User name", max_length=30,
                                regex=r'^[\w.@+-]+$',
                                error_messages={'invalid': "This value may "
                                "contain only letters, numbers and @/./+/-/_ "
                                "characters."},
                                help_text=u"Enter your user name, with no spaces or special characters. Your user name is used for your login, and is case sensitive.",
                                widget=forms.TextInput(attrs={"size": 30,
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

    email = forms.EmailField(label=u"Email:", max_length=75,
                             help_text=u"Enter your email address. This is "
                             "used to confirm your registration, so please "
                             "use a valid email address. We respect your "
                             "privacy, and will not share your information "
                             "with third parties.",
                             widget=forms.TextInput(attrs={"size": 40,
                                                           "class": "text"}))

    confirm_email = forms.EmailField(label=u"Confirm email", max_length=75,
                             help_text=u"Re-enter your email address.",
                             widget=forms.TextInput(attrs={"size": 40,
                                                           "class": "text"}))

    role = forms.ChoiceField(choices=((u"", u"Select one"),) + MEMBER_ROLES,
                             required=False,
                             label="Role:",
                             help_text=u"Indicate your relationship to open "
                             "educational resources.")

    newsletter = forms.BooleanField(label=u"Subscribe to the OER Commons Monthly Newsletter",
                                    widget=forms.CheckboxInput(),
                                    required=False,
                                    initial=True)

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password", "")
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise forms.ValidationError(u"The two passwords do not match.")
        return confirm_password

    def clean_confirm_email(self):
        email = self.cleaned_data.get("email", "")
        confirm_email = self.cleaned_data["confirm_email"]
        if email != confirm_email:
            raise forms.ValidationError(u"The two emails do not match.")
        return confirm_email


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
            username = data["username"]
            email = data["email"]
            username_taken = False
            username_pending = False
            email_taken = False
            email_pending = False
            if User.objects.filter(username=username).count():
                username_taken = True
                user = User.objects.get(username=username)
                if RegistrationConfirmation.objects.filter(user=user, confirmed=False).count():
                    username_pending = True
            if User.objects.filter(email=email).count():
                email_taken = True
                user = User.objects.get(email=email)
                if RegistrationConfirmation.objects.filter(user=user, confirmed=False).count():
                    email_pending = True

            if username_pending or email_pending:
                resend_confirmation_url = reverse("users:registration_resend")
                if username_pending and email_pending:
                    message = u"A registration request for the user account with username <em>%(username)s</em> and email <em>%(email)s</em> needs to be confirmed. <a href=\"%(url)s?username=%(username)s&amp;email=%(email)s\">Click here</a> to re-send the confirmation email."
                    message = message % dict(username=username, email=email,
                                             url=resend_confirmation_url)
                elif username_pending:
                    message = u"A registration request for the user account with username <em>%(username)s</em> needs to be confirmed. <a href=\"%(url)s?username=%(username)s\">Click here</a> to re-send the confirmation email."
                    message = message % dict(username=username,
                                             url=resend_confirmation_url)
                else:
                    message = u"A registration request for the user account with email <em>%(email)s</em> needs to be confirmed. <a href=\"%(url)s?email=%(email)s\">Click here</a> to re-send the confirmation email."
                    message = message % dict(email=email,
                                             url=resend_confirmation_url)
                messages.warning(request, message)
                return direct_to_template(request, "users/registration.html", locals())

            elif username_taken or email_taken:
                reset_password_url = reverse("users:reset_password_init")
                if username_taken and email_taken:
                    message = u"User with username <em>%(username)s</em> and email <em>%(email)s</em> is registered already. If you forgot your password you can <a href=\"%(url)s\"> click here</a> to reset it. "
                    message = message % dict(username=username, email=email,
                                             url=reset_password_url)
                elif username_taken:
                    message = u"User with username <em>%(username)s</em> is registered already. If you forgot your password you can <a href=\"%(url)s\">click here</a> to reset it."
                    message = message % dict(username=username,
                                             url=reset_password_url)
                else:
                    message = u"User with email <em>%(email)s</em> is registered already. If you forgot your password you can <a href=\"%(url)s\">click here</a> to reset it."
                    message = message % dict(email=email,
                                             url=reset_password_url)
                messages.warning(request, message)
                return direct_to_template(request, "users/registration.html", locals())

            else:
                try:
                    first_name, last_name = data["name"].split(None, 1)
                except ValueError:
                    first_name = data["name"]
                    last_name = u""
                password = encrypt_password(data["password"])
                user = User(username=username, first_name=first_name,
                            last_name=last_name, email=email,
                            password=password, is_active=False)
                user.save()
                profile = Profile(user=user, role=data["role"])
                profile.save()
                confirmation = RegistrationConfirmation(user=user,
                                                        confirmed=False)
                confirmation.save()
                confirmation.send_confirmation()
                
                if data["newsletter"]:
                    api_key = getattr(settings, "MAILCHIMP_API_KEY", None)
                    list_id = getattr(settings, "MAILCHIMP_LIST_ID", None)
                    
                    if api_key and list_id:
                        try:
                            list = mailchimp.utils.get_connection().get_list_by_id(list_id)
                            user_data = {"EMAIL": email}
                            if first_name:
                                user_data["FNAME"] = first_name
                            if last_name:
                                user_data["LNAME"] = last_name
                            list.subscribe(email, user_data)
                        except:
                            pass
                
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
