from materials.models.common import License


class LicenseFields:
    
    def clean_license(self):
        name = self.cleaned_data.get("license_name")
        url = self.cleaned_data.get("license_url")
        description = self.cleaned_data.get("license_description")
        copyright_holder = self.cleaned_data.get("copyright_holder")
        bucket = self.cleaned_data.get("cou_bucket")
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
        self.fields["license_name"].initial = license.name
        self.fields["license_url"].initial = license.url
        self.fields["license_description"].initial = license.description
        self.fields["copyright_holder"].initial = license.copyright_holder
        self.fields["cou_bucket"].initial = license.bucket
