from django import forms
from django.forms.models import ModelForm, save_instance
from django.forms.widgets import RadioFieldRenderer
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from materials.models.common import GeneralSubject, GradeLevel, License, \
    PUBLIC_DOMAIN_URL, PUBLIC_DOMAIN_NAME, GNU_FDL_URL, GNU_FDL_NAME, \
    CC_LICENSE_URL_RE, Author, Keyword


LICENSE_TYPES = (
  (u"cc", u"Creative Commons License (Latest Version)"),
  (u"cc-old", u"Creative Commons License (Previous Versions)"),
  (u"public-domain", u"Public Domain"),
  (u"gnu-fdl", u"GNU Free Documentation License"),
  (u"custom", u"Custom Permissions"),
)

CC_OLD_LICENSES = (
    (u"-", u"-- select license--"),
    (u"http://creativecommons.org/licenses/by/1.0/", u"Creative Commons Attribution 1.0"),
    (u"http://creativecommons.org/licenses/by-sa/1.0/", u"Creative Commons Attribution-Share Alike 1.0"),
    (u"http://creativecommons.org/licenses/by-nd/1.0/", u"Creative Commons Attribution-No Derivative Works 1.0"),
    (u"http://creativecommons.org/licenses/by-nc/1.0/", u"Creative Commons Attribution-Noncommercial 1.0"),
    (u"http://creativecommons.org/licenses/by-nc-sa/1.0/", u"Creative Commons Attribution-Noncommercial-Share Alike 1.0"),
    (u"http://creativecommons.org/licenses/by-nc-nd/1.0/", u"Creative Commons Attribution-Noncommercial-No Derivative Works 1.0"),
    (u"http://creativecommons.org/licenses/by/2.0/", u"Creative Commons Attribution 2.0"),
    (u"http://creativecommons.org/licenses/by-sa/2.0/", u"Creative Commons Attribution-Share Alike 2.0"),
    (u"http://creativecommons.org/licenses/by-nd/2.0/", u"Creative Commons Attribution-No Derivative Works 2.0"),
    (u"http://creativecommons.org/licenses/by-nc/2.0/", u"Creative Commons Attribution-Noncommercial 2.0"),
    (u"http://creativecommons.org/licenses/by-nc-sa/2.0/", u"Creative Commons Attribution-Noncommercial-Share Alike 2.0"),
    (u"http://creativecommons.org/licenses/by-nc-nd/2.0/", u"Creative Commons Attribution-Noncommercial-No Derivative Works 2.0"),
    (u"http://creativecommons.org/licenses/by/2.5/", u"Creative Commons Attribution 2.5"),
    (u"http://creativecommons.org/licenses/by-sa/2.5/", u"Creative Commons Attribution-Share Alike 2.5"),
    (u"http://creativecommons.org/licenses/by-nd/2.5/", u"Creative Commons Attribution-No Derivative Works 2.5"),
    (u"http://creativecommons.org/licenses/by-nc/2.5/", u"Creative Commons Attribution-Noncommercial 2.5"),
    (u"http://creativecommons.org/licenses/by-nc-sa/2.5/", u"Creative Commons Attribution-Noncommercial-Share Alike 2.5"),
    (u"http://creativecommons.org/licenses/by-nc-nd/2.5/", u"Creative Commons Attribution-Noncommercial-No Derivative Works 2.5"),
)

class AuthorsField(forms.Field):

    widget = forms.TextInput

    def prepare_value(self, value):
        if not value:
            return u""
        if isinstance(value, basestring):
            return value
        if isinstance(value, list):
            value = Author.objects.filter(id__in=value)
        return u", ".join(value.values_list("name", flat=True))

    def to_python(self, value):
        if value is None:
            return []
        values = sorted(set([v.strip() for v in value.split(u",") if v.strip()]))
        return [{"name": v} for v in values]


class KeywordsWidget(forms.Textarea):

    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = u"\n".join(value)
        return super(KeywordsWidget, self).render(name, value, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        values = []
        if isinstance(data, (MultiValueDict, MergeDict)):
            values = data.getlist(name + "_suggested")
        else:
            values = data.get(name + "_suggested", [])
        values += data.get(name, u"").split("\n")
        return values


class KeywordsField(forms.Field):

    widget = KeywordsWidget

    def prepare_value(self, value):
        if not value:
            return u""
        if isinstance(value, list):
            values = []
            for v in value:
                if isinstance(v, int):
                    values.append(Keyword.objects.get(id=v).name)
                else:
                    values.append(v)
            return values
        return list(value.values_list("name", flat=True))

    def to_python(self, value):
        values = sorted(set([v.strip() for v in value if v.strip()]))
        return [{"name": v} for v in values]


class LicenseTypeFieldRenderer(RadioFieldRenderer):

    def render(self):
        return mark_safe(u'\n'.join([u'<div class="radio">%s</div>'
                % force_unicode(w) for w in self]))


class RSSFields:

    def clean_rss_description(self):
        value = self.cleaned_data["rss_description"]
        if self.cleaned_data.get("in_rss") and not value:
            raise forms.ValidationError(u"This field is required.")
        return value

    def clean_rss_timestamp(self):
        value = self.cleaned_data["rss_timestamp"]
        if self.cleaned_data.get("in_rss") and not value:
            raise forms.ValidationError(u"This field is required.")
        return value


class SubmissionFormBase(RSSFields):

    def _post_clean(self):
        pass

    def save(self, commit=True):
        """
        Saves this ``form``'s cleaned_data into model instance
        ``self.instance``.

        If commit=True, then the changes to ``instance`` will be saved to the
        database. Returns ``instance``.
        """
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'
        return save_instance(self, self.instance, self._meta.fields,
                             fail_message, commit, construct=True)

    def clean_license_cc(self):
        value = self.cleaned_data["license_cc"]
        if self.cleaned_data.get("license_type") == "cc":
            if not value:
                raise forms.ValidationError(u"You should select the license.")
            if not CC_LICENSE_URL_RE.match(value):
                raise forms.ValidationError(u"Invalid license URL.")
        else:
            return u""
        return value

    def clean_license_cc_old(self):
        value = self.cleaned_data["license_cc_old"]
        if self.cleaned_data.get("license_type") == "cc-old":
            if not value or value == "-":
                raise forms.ValidationError(u"You should select the license.")
        else:
            return u""
        return value

    def clean_license_custom_name(self):
        value = self.cleaned_data["license_custom_name"]
        if self.cleaned_data.get("license_type") == "custom":
            if not value:
                raise forms.ValidationError(u"This field is required.")
        else:
            return u""
        return value

    def clean_license(self):
        license_type = self.cleaned_data.get("license_type")
        if not license_type:
            raise forms.ValidationError(u"You should select the type of license.")
        url = None
        name = None
        if license_type == "cc":
            url = self.cleaned_data.get("license_cc")
            if url:
                name = License.objects.get_cc_license_name_from_url(url)
        elif license_type == "cc-old":
            url = self.cleaned_data.get("license_cc_old")
            if url:
                name = License.objects.get_cc_license_name_from_url(url)
        elif license_type == "public-domain":
            url = PUBLIC_DOMAIN_URL
            name = PUBLIC_DOMAIN_NAME
        elif license_type == "gnu-fdl":
            url = GNU_FDL_URL
            name = GNU_FDL_NAME
        elif license_type == "custom":
            url = self.cleaned_data.get("license_custom_url")
            name = self.cleaned_data.get("license_custom_name")
        description = self.cleaned_data.get("license_description")
        copyright_holder = self.cleaned_data.get("copyright_holder")
        if "cou_bucket" in self.cleaned_data:
            bucket = self.cleaned_data["cou_bucket"]
        else:
            bucket = None
        license = {}
        if url:
            license["url"] = url
        if name:
            license["name"] = name
        if description:
            license["description"] = description
        if copyright_holder:
            license["copyright_holder"] = copyright_holder
        if bucket:
            license["bucket"] = bucket
        return license

    def set_initial_license_data(self):
        instance = getattr(self, "instance", None)
        if instance is None:
            return
        try:
            license = instance.license
        except License.DoesNotExist:
            return
        if license.type.startswith("cc-"):
            if license.url in [l[0] for l in CC_OLD_LICENSES]:
                self.fields["license_type"].initial = "cc-old"
                self.fields["license_cc_old"].initial = license.url
            else:
                self.fields["license_type"].initial = "cc"
                self.fields["license_cc"].initial = license.url
        elif license.type == "public-domain":
            self.fields["license_type"].initial = "public-domain"
        elif license.type == "gnu-fdl":
            self.fields["license_type"].initial = "gnu-fdl"
        elif license.type == "custom":
            self.fields["license_type"].initial = "custom"
            self.fields["license_custom_name"].initial = license.name
            self.fields["license_custom_url"].initial = license.url
        self.fields["license_description"].initial = license.description
        self.fields["copyright_holder"].initial = license.copyright_holder
        if "cou_bucket" in self.fields:
            self.fields["cou_bucket"].initial = license.bucket
