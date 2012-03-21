from authoring.models import AuthoredMaterialDraft
from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from materials.models.common import CC_LICENSE_URL_RE, License, Keyword
from itertools import chain
from core.forms import MultipleAutoCreateField, AutocompleteListWidget
from django.forms import ModelMultipleChoiceField
from django.forms.widgets import CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from materials.models import GeneralSubject, Language
import string


class LearningGoalsWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        if not value: value = []
        existing = []
        for v in value:
            existing.append((v, forms.TextInput().render(name, v, attrs)))
        return render_to_string("authoring/forms/learning-goals-widget.html", dict(
            existing=existing,
            new=forms.TextInput().render(name, u"", attrs)
        ))

    def value_from_datadict(self, data, files, name):
        return filter(bool, map(string.strip, data.getlist(name)))


class SubjectsWidget(forms.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            if i == (len(self.choices) / 2):
                output.append(u'</ul>')
                output.append(u'<ul>')

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


class LicenseWidget(forms.Widget):

    DERIVATIVES_CHOICES = (
        (u"y", "Yes, allow"),
        (u"sa", "Yes, allow as long as others share alike"),
        (u"n", "No, do not allow"),
    )

    COMMERCIAL_CHOICES = (
        (u"y", "Yes, allow"),
        (u"n", "No, do not allow"),
    )

    def value_from_datadict(self, data, files, name):
        return data.get("%s_url" % name)

    def render(self, name, value, attrs=None):
        license_url = value.get("url", u"")
        license_name = value.get("name", u"")
        derivatives = u""
        commercial = u""

        r = CC_LICENSE_URL_RE.search(license_url)
        if r:
            cc_type = r.groupdict()["cc_type"]
            if "nd" in cc_type:
                derivatives = "n"
            elif "sa" in cc_type:
                derivatives = "sa"
            else:
                derivatives = "y"
            commercial = "n" if "nc" in cc_type else "y"
        else:
            cc_type = ""
            license_url = u""
            license_name = u""

        return mark_safe(render_to_string(
            "authoring/forms/license-widget.html",
            dict(
                name=name,
                cc_type=cc_type,
                name_widget=forms.HiddenInput().render("%s_name" % name, license_name),
                url_widget=forms.HiddenInput().render("%s_url" % name, license_url),
                derivatives_widget=forms.RadioSelect().render(
                    "%s_derivatives" % name,
                    derivatives,
                    choices=self.DERIVATIVES_CHOICES,
                ),
                commercial_widget=forms.RadioSelect().render(
                    "%s_commercial" % name,
                    commercial,
                    choices=self.COMMERCIAL_CHOICES,
                )
            )
        ))


class LicenseField(forms.Field):

    widget = LicenseWidget
    default_error_messages = {
        'required': _(u'Please select a license.'),
        'invalid': _(u'Invalid license URL.'),
    }

    def prepare_value(self, value):
        if not value:
            return {}
        if hasattr(value, '_meta'):
            value = value.serializable_value("url")
        else:
            value = value
        name = License.objects.get_cc_license_name_from_url(value) if CC_LICENSE_URL_RE.match(value) else u""
        return dict(url=value, name=name)

    def to_python(self, value):
        if not value:
            return None
        if not CC_LICENSE_URL_RE.match(value):
            raise forms.ValidationError(self.default_error_messages["invalid"])
        return dict(url=value, name=License.objects.get_cc_license_name_from_url(value))


class EditForm(forms.ModelForm):

    # TODO: clean up HTML from `text` field.
    # using lxml clean. Remove all styles, Keep only allowed classes,
    # remove scripts, styles, forms, iframes, objects, embeds

    learning_goals = MultipleAutoCreateField("title", widget=LearningGoalsWidget())
    keywords = MultipleAutoCreateField("name", widget=AutocompleteListWidget(Keyword, "name"), required=False)
    subjects = ModelMultipleChoiceField(GeneralSubject.objects.all(), widget=SubjectsWidget())
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)
    license = LicenseField()

    def __init__(self, *args, **kwargs):
        not_required = kwargs.pop("not_required", False)
        update_published = kwargs.pop("update_published", False)
        super(EditForm, self).__init__(*args, **kwargs)
        if not_required:
            for field in self.fields.values():
                field.required = False

        if update_published:
            # We don't allows to change the license after the material was published
            del self.fields["license"]
            #noinspection PyUnresolvedReferences
            self._meta.fields = [f for f in self._meta.fields if f != "license"]

    class Meta:
        model = AuthoredMaterialDraft
        fields = ["title", "text", "summary", "learning_goals", "keywords", "subjects", "grade_level", "language", "license"]
        widgets = dict(
            title=forms.HiddenInput(),
            text=forms.HiddenInput(),
            summary=forms.Textarea(attrs=dict(
                placeholder=u"Please give a short summary of your resource. This will appear as the preview in search results."
            ))
        )
