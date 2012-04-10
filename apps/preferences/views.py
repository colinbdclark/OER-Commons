from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from preferences.models import Preferences, PREFERENCE_FIELDS
import json


class PreferencesForm(forms.models.ModelForm):

    success_message = u"You preferences were saved."
    error_message = u"Please correct the indicated errors."

    show_toolbar = forms.BooleanField(label=u"Show OER Commons toolbar when viewing resources.",
                                      widget=forms.CheckboxInput(),
                                      required=False)

    class Meta:
        model = Preferences
        fields = PREFERENCE_FIELDS.keys()


def get_preferences_from_cookies(request):
    preferences = {}
    for field_name, (cookie_name, default_value) in PREFERENCE_FIELDS.items():
        value = default_value
        cookie_value = request.COOKIES.get(cookie_name, None)
        if cookie_value:
            try:
                value = json.loads(cookie_value)
            except ValueError:
                pass
        preferences[field_name] = value

    return preferences


def save_preferences_to_cookies(response, data):
    max_age = 3600 * 24 * 365 * 2 # Two years
    for field_name, value in data.items():
        if field_name not in PREFERENCE_FIELDS:
            continue
        cookie_name = PREFERENCE_FIELDS[field_name][0]
        value = json.dumps(value)
        response.set_cookie(cookie_name, value, max_age=max_age)


def delete_preference_cookies(response):
    for cookie_name, default_value in PREFERENCE_FIELDS.values():
        response.delete_cookie(cookie_name)


def preferences(request):

    page_title = u"My Preferences"

    user = request.user.is_authenticated() and request.user or None
    instance = None
    if user:
        try:
            instance = Preferences.objects.get(user=user)
        except Preferences.DoesNotExist:
            pass
    if instance:
        form = PreferencesForm(instance=user)
    else:
        form = PreferencesForm(initial=get_preferences_from_cookies(request))

    if request.method == "POST":
        if user:
            if not instance:
                instance = Preferences(user=user)
            form = PreferencesForm(request.POST, instance=instance)
            if form.is_valid():
                instance = form.save()
                messages.success(request, form.success_message)
                form = PreferencesForm(instance=instance)
                response = direct_to_template(request, "preferences/preferences.html", locals())
                delete_preference_cookies(response)
                return response
            else:
                messages.error(request, form.error_message)
        else:
            form = PreferencesForm(request.POST)
            if form.is_valid():
                messages.success(request, form.success_message)
                data = form.cleaned_data
                form = PreferencesForm(initial=data)
                response = direct_to_template(request, "preferences/preferences.html", locals())
                save_preferences_to_cookies(response, data)
                return response
            else:
                messages.error(request, form.error_message)

    return direct_to_template(request, "preferences/preferences.html", locals())