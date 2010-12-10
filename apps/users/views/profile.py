from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template
from materials.models.common import GradeLevel
from users.backend import encrypt_password
from users.models import Profile, MEMBER_ROLES
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse


class ProfileForm(forms.ModelForm):

    name = forms.CharField(max_length=61, label=u"Your name:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    email = forms.EmailField(label=u"Email:",
                             widget=forms.TextInput(attrs={"class": "text"}))

    homepage = forms.URLField(label=u"Homepage:",
                              required=False,
                              widget=forms.TextInput(attrs={"class": "text"}))

    institution = forms.CharField(label=u"Institution:",
                                  required=False,
                                  widget=forms.TextInput(
                                                     attrs={"class": "text"}))

    institution_url = forms.URLField(label=u"Institution URL:",
                                     required=False,
                                     widget=forms.TextInput(
                                                    attrs={"class": "text"}))

    state = forms.CharField(label=u"State, Province, or Country:",
                            required=False,
                            widget=forms.TextInput(attrs={"class": "text"}))

    role = forms.ChoiceField(choices=((u"", u"Select one"),) + MEMBER_ROLES,
                             required=False,
                             label="Role:",
                             help_text=u"Indicate your relationship to open "
                             "educational resources.")

    grade_level = forms.ModelMultipleChoiceField(GradeLevel.objects.all(),
                            required=False,
                            label=u"Grade Level:",
                            widget=forms.CheckboxSelectMultiple())

    department = forms.CharField(label=u"Department and/or Subject areas in "
                                 "which you are involved:",
                                 required=False,
                                 widget=forms.Textarea(attrs={"class":"text"}))

    specializations = forms.CharField(label=u"Specializations/Interests:",
                                 required=False,
                                 widget=forms.Textarea(attrs={"class":"text"}))

    biography = forms.CharField(label=u"Biography:",
                                 required=False,
                                 widget=forms.Textarea(attrs={"class":"text"}))

    why_interested = forms.CharField(label=u"Why are you interested in open "
                                "educational resources?",
                                 required=False,
                                 widget=forms.Textarea(attrs={"class":"text"}))

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance is not None:
            user = self.instance.user
            name = ("%s %s" % (user.first_name, user.last_name)).strip()
            self.fields["name"].initial = name
            self.fields["email"].initial = user.email

    def save(self, *args, **kwargs):
        super(ProfileForm, self).save(*args, **kwargs)
        name = self.cleaned_data["name"]
        try:
            first_name, last_name = name.split(None, 1)
        except ValueError:
            first_name = name
            last_name = u""
        user = self.instance.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = self.cleaned_data["email"]
        user.save()

    def clean_email(self):
        email = self.cleaned_data["email"]
        instance = getattr(self, "instance", None)
        if instance is not None:
            if User.objects.filter(email=email).exclude(
                                                pk=instance.user.id).count():
                raise forms.ValidationError(u"This email address is used by "
                                            "another user.")
        return email

    class Meta:
        model = Profile
        fields = ["name", "email", "homepage", "institution",
                  "institution_url", "state", "role", "grade_level",
                  "department", "specializations", "biography",
                  "why_interested"]


class ChangePasswordForm(forms.ModelForm):

    current_password = forms.CharField(min_length=5,
                                       label=u"Current password:",
                           widget=forms.PasswordInput(attrs={"class": "text",
                                                     "autocomplete": "off"}))

    new_password = forms.CharField(min_length=5, label=u"New password:",
                           widget=forms.PasswordInput(attrs={"class": "text",
                                                     "autocomplete": "off"}))

    confirm_new_password = forms.CharField(min_length=5,
                                           label=u"Confirm new password:",
                           widget=forms.PasswordInput(attrs={"class": "text",
                                                     "autocomplete": "off"}))

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]
        instance = getattr(self, "instance", None)
        if instance is not None:
            if authenticate(username=instance.username,
                            password=current_password) is None:
                raise forms.ValidationError(u"Wrong password")
        return current_password

    def clean_confirm_new_password(self):
        password = self.cleaned_data.get("new_password", "")
        confirm_password = self.cleaned_data["confirm_new_password"]
        if password != confirm_password:
            raise forms.ValidationError(u"The two passwords do not match.")
        return confirm_password

    def save(self, *args, **kwargs):
        super(ChangePasswordForm, self).save(*args, **kwargs)
        user = self.instance
        user.password = encrypt_password(self.cleaned_data["new_password"])
        user.save()

    class Meta:
        model = User
        fields = ["current_password", "new_password", "confirm_new_password"]


@login_required
def profile(request):

    page_title = u"My Profile"
    breadcrumbs = [{"url": reverse("users:profile"), "title": page_title}]

    user = request.user
    profile_form = ProfileForm(instance=user.profile)
    change_password_form = ChangePasswordForm()

    if request.method == "POST" and "save-profile" in request.POST:
        profile_form = ProfileForm(request.POST, instance=user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, u"Your profile was saved.")
        else:
            messages.error(request, u"Please correct the indicated errors.")
    elif request.method == "POST" and "change-password" in request.POST:
        change_password_form = ChangePasswordForm(request.POST,
                                                  instance=user)
        if change_password_form.is_valid():
            change_password_form.save()
            body = render_to_string("users/emails/change-password.html",
                                    dict(user=user,
               new_password=change_password_form.cleaned_data["new_password"],
               domain=Site.objects.get_current().domain))
            message = EmailMessage(u"OER Commons: Password Changed",
                                   body, None, [user.email])
            message.content_subtype = "html"
            message.send()
            messages.success(request, u"Your password was changed.")
            change_password_form = ChangePasswordForm()
        else:
            messages.error(request, u"Please correct the indicated errors.")

    return direct_to_template(request, "users/profile.html", locals())

