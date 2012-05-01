from materials.models.course import RelatedMaterial


class DerivedFields:

    def clean_derived_from(self):
        if not self.cleaned_data.get("derived"):
            return None
        data = {}
        for field in ("title", "url", "description"):
            value = self.cleaned_data.get("derived_%s" % field)
            if value:
                data[field] = value
        if not data:
            return None
        return data

    def set_initial_derived_data(self):
        instance = getattr(self, "instance", None)
        if instance is None:
            return
        try:
            derived_from = instance.derived_from
        except RelatedMaterial.DoesNotExist:
            return
        if derived_from is None:
            return
        self.fields["derived"].initial = True
        self.fields["derived_title"].initial = derived_from.title
        self.fields["derived_url"].initial = derived_from.url
        self.fields["derived_description"].initial = derived_from.description


class PrePostRequisitesFields:

    def _clean_requisite(self, kind, number):
        if not self.cleaned_data.get("has_%srequisites" % kind):
            return None
        data = {}
        for field in ("title", "url"):
            value = self.cleaned_data.get("%srequisite_%i_%s" % (kind, number, field))
            if value:
                data[field] = value
        if not data:
            return None
        return data

    def clean_prerequisite_1(self):
        return self._clean_requisite("pre", 1)

    def clean_prerequisite_2(self):
        return self._clean_requisite("pre", 2)

    def clean_postrequisite_1(self):
        return self._clean_requisite("post", 1)

    def clean_postrequisite_2(self):
        return self._clean_requisite("post", 2)

    def _set_initial_requisite_data(self, kind, number):
        instance = getattr(self, "instance", None)
        if instance is None:
            return
        try:
            requisite = getattr(instance, "%srequisite_%i" % (kind, number))
        except RelatedMaterial.DoesNotExist:
            return
        if requisite is None:
            return
        self.fields["has_%srequisites" % kind].initial = True
        self.fields["%srequisite_%i_title" % (kind, number)].initial = requisite.title
        self.fields["%srequisite_%i_url" % (kind, number)].initial = requisite.url

    def set_initial_requisite_data(self):
        for kind in ("pre", "post"):
            for number in (1, 2):
                self._set_initial_requisite_data(kind, number)

