from authoring.models import AuthoredMaterialDraft
from authoring.views import EditMaterialProcessForm
from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from materials.models.common import CC_LICENSE_URL_RE, License


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
            license_url = u""
            license_name = u""

        return mark_safe(render_to_string(
            "authoring/include/license-widget.html",
            dict(
                name=name,
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
        if value:
            if not CC_LICENSE_URL_RE.match(value):
                raise forms.ValidationError(self.default_error_messages["invalid"])
            value = dict(url=value, name=License.objects.get_cc_license_name_from_url(value))
        return value


class SubmitForm(forms.ModelForm):

    license = LicenseField()

    class Meta:
        model = AuthoredMaterialDraft
        fields = ["license"]


class Submit(EditMaterialProcessForm):

    form_class = SubmitForm
