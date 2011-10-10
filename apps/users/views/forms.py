from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from geo.models import Country, USState
from users.backend import encrypt_password
from users.models import Profile, CONNECT_OPTIONS, Role, StudentLevel, \
    EducatorSubject, FACEBOOK_URL_RE, TWITTER_URL_RE
from utils.forms import AutocompleteListField, AutocompleteListWidget


class UserInfoForm(forms.ModelForm):

    success_message = u"Your profile was saved."
    error_message = u"Please correct the indicated errors."

    first_name = forms.CharField(max_length=30, label=u"First name:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    last_name = forms.CharField(max_length=30, label=u"Last name:",
                           widget=forms.TextInput(attrs={"class": "text"}))

    email = forms.EmailField(label=u"Email:",
                             widget=forms.TextInput(attrs={"class": "text"}))

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
        fields = ["first_name", "last_name", "email"]


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


class AvatarForm(forms.Form):

    file = forms.ImageField()


class GeographyForm(forms.ModelForm):

    success_message = u"Your geography information was saved."
    error_message = u"Please correct the indicated errors."

    country = forms.ModelChoiceField(Country.objects.all(),
                                     label=u"Country:",
                                     to_field_name="code",
                                     required=False)

    us_state = forms.ModelChoiceField(USState.objects.all(),
                                      label=u"State:",
                                      to_field_name="code",
                                      required=False)

    connect_with = forms.ChoiceField(choices=CONNECT_OPTIONS,
                                        widget=forms.RadioSelect(),
                                        label=u"",
                                        required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        country = cleaned_data.get("country")
        if not country or country.code != "US":
            cleaned_data["us_state"] = None
        return cleaned_data

    class Meta:
        model = Profile
        fields = ["country", "us_state", "connect_with"]


class RolesForm(forms.ModelForm):

    success_message = u"Your roles were saved."
    error_message = u"Please correct the indicated errors."

    roles = forms.ModelMultipleChoiceField(Role.objects.all(),
                                     label=u"Which of these roles best describe you? Check all that apply.",
                                     required=False,
                                     widget=forms.CheckboxSelectMultiple())

    educator_student_levels = forms.ModelMultipleChoiceField(StudentLevel.objects.all(),
                                     label=u"I teach students at the following levels. Check all that apply.",
                                     required=False,
                                     widget=forms.CheckboxSelectMultiple())

    educator_subjects = AutocompleteListField(model=EducatorSubject,
                                              autocomplete_field="title",
                                              label=u"I teach my students the following subjects:",
                                              widget=AutocompleteListWidget(new_item_label=u"Add subject"),
                                              required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        roles = cleaned_data.get("roles")
        if roles:
            is_educator = any([role.is_educator for role in roles])
            if not is_educator:
                cleaned_data["educator_student_levels"] = []
        return cleaned_data

    class Meta:
        model = Profile
        fields = ["roles", "educator_student_levels", "educator_subjects"]


class AboutMeForm(forms.ModelForm):

    success_message = u"Your profile was saved."
    error_message = u"Please correct the indicated errors."

    about_me = forms.CharField(label=u"About me",
                               required=False,
                               widget=forms.Textarea(attrs={"class": "text"}))

    website_url = forms.URLField(label=u"Website or blog",
                                 widget=forms.TextInput(
                                    attrs={"placeholder": "http://",
                                           "class": "text"}),
                                 required=False)

    facebook_id = forms.CharField(label=u"Facebook Profile", required=False,
                                  widget=forms.TextInput(
                                      attrs={"class": "text",
                   "placeholder": "https://www.facebook.com/your_username"}))

    twitter_id = forms.CharField(label=u"Twitter", required=False,
                                 widget=forms.TextInput(attrs={"class": "text"}))

    skype_id = forms.CharField(label=u"Skype", required=False,
                               widget=forms.TextInput(attrs={"class": "text"}))

    def __init__(self, *args, **kwargs):
        super(AboutMeForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.facebook_id and self.instance.facebook_id.isdigit():
            self.initial["facebook_id"] = self.instance.facebook_url

    def clean_facebook_id(self):
        facebook_id = self.cleaned_data["facebook_id"]
        r = FACEBOOK_URL_RE.search(facebook_id)
        if r:
            facebook_id = r.groupdict()["facebook_id"]
        return facebook_id

    def clean_twitter_id(self):
        twitter_id = self.cleaned_data["twitter_id"]
        r = TWITTER_URL_RE.search(twitter_id)
        if r:
            twitter_id = r.groupdict()["twitter_id"]
        return twitter_id

    class Meta:
        model = Profile
        fields = ["about_me", "website_url", "facebook_id", "twitter_id",
                  "skype_id"]
