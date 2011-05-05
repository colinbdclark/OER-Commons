from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template
from users.backend import encrypt_password
from users.models import Profile
from utils.decorators import login_required
from utils.shortcuts import ajax_form_success, ajax_form_error


class UserInfoForm(forms.ModelForm):

    success_mesage = u"Your profile was saved."
    error_message = u"Please correct the indicated errors."

    first_name = forms.CharField(max_length=30, label=u"First name:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    last_name = forms.CharField(max_length=30, label=u"Last name:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    username = forms.CharField(max_length=30, label=u"Username:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    email = forms.EmailField(label=u"Email:",
                             widget=forms.TextInput(attrs={"class": "text"}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        instance = getattr(self, "instance", None)
        if instance is not None:
            if User.objects.filter(username=username).exclude(pk=instance.id).exists():
                raise forms.ValidationError(u"This username is used by "
                                            "another user.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        instance = getattr(self, "instance", None)
        if instance is not None:
            if User.objects.filter(email=email).exclude(pk=instance.id).exists():
                raise forms.ValidationError(u"This email address is used by "
                                            "another user.")
        return email

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]


class ChangePasswordForm(forms.ModelForm):

    success_message = u"Your password was changed. New password was emailed to you."
    error_message = u"Please correct the indicated errors."

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
    profile = Profile.objects.get_or_create(user=user)[0]
    user_info_form = UserInfoForm(instance=user)
    change_password_form = ChangePasswordForm()

    if request.method == "POST":
        
        if "user-info" in request.POST:
            user_info_form = UserInfoForm(request.POST, instance=user)
            
            if user_info_form.is_valid():
                user_info_form.save()
                
                if request.is_ajax():
                    return ajax_form_success(user_info_form.success_mesage)
                
                messages.success(request, user_info_form.success_mesage)
                
            else:
                if request.is_ajax():
                    return ajax_form_error(user_info_form, user_info_form.error_message)
                
                messages.error(request, user_info_form.error_message)
                    
        elif "change-password" in request.POST:
            change_password_form = ChangePasswordForm(request.POST, instance=user)
            
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
                
                if request.is_ajax():
                    return ajax_form_success(change_password_form.success_message)
                
                messages.success(request, change_password_form.success_message)
                change_password_form = ChangePasswordForm()
                
            else:
                if request.is_ajax():
                    return ajax_form_error(change_password_form,
                                           change_password_form.error_message)
                    
                messages.error(request, change_password_form.error_message)

    return direct_to_template(request, "users/profile.html", locals())

