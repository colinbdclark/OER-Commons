from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from geo.models import Country
from users.backend import encrypt_password
from users.models import Profile, CONNECT_OPTIONS, Role, StudentLevel, \
    EducatorSubject
from utils.forms import AutocompleteListField, AutocompleteListWidget


class UserInfoForm(forms.ModelForm):

    success_mesage = u"Your profile was saved."
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
    
    connect_with = forms.ChoiceField(choices=CONNECT_OPTIONS,
                                        widget=forms.RadioSelect(),
                                        label=u"",
                                        required=False)
    
    class Meta:
        model = Profile
        fields = ["country", "connect_with"]


class RolesForm(forms.ModelForm):

    success_message = u"Your roles were saved."
    error_message = u"Please correct the indicated errors."
    
    roles = forms.ModelMultipleChoiceField(Role.objects.all(),
                                     label=u"Which of these roles best describe you? Check all that apply.",
                                     required=False,
                                     widget=forms.CheckboxSelectMultiple())

    educator_student_levels = forms.ModelMultipleChoiceField(StudentLevel.objects.all(),
                                     label=u"I teach students at the following levels (check all that apply):",
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
            is_educator = reduce(lambda x, y: getattr(x, "is_educator", x) or \
                                              getattr(y, "is_educator", y),
                                 roles, False)
            if not is_educator:
                cleaned_data["educator_student_levels"] = []
        return cleaned_data
    
    class Meta:
        model = Profile
        fields = ["roles", "educator_student_levels", "educator_subjects"]


class AboutMeForm(forms.ModelForm):

    success_message = u"Your profile was saved."
    error_message = u"Please correct the indicated errors."
    
    about_me = forms.CharField(label=u"",
                               required=False,
                               widget=forms.Textarea)
    
    class Meta:
        model = Profile
        fields = ["about_me"]
        