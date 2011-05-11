from django import forms
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


class AutocompleteListWidget(forms.Textarea):

    def render(self, name, value, attrs=None):
        opts = self.model._meta
        app_label = opts.app_label
        model_name = opts.object_name.lower()
        autocomplete_url = reverse("utils:autocomplete",
                                   args=(app_label, model_name, 
                                    self.autocomplete_field))
        new_item_label = opts.verbose_name.lower()
        if value and not isinstance(value, list):
            value = [value]
        return render_to_string("utils/include/autocomplete-list-widget.html",
                                dict(name=name, value=value, attrs=attrs,
                                     autocomplete_url=autocomplete_url,
                                     new_item_label=new_item_label))

    def value_from_datadict(self, data, files, name):
        values = [k for k in data.get(name, u"").split(",") if k]
        return values


class AutocompleteListField(forms.Field):

    widget = AutocompleteListWidget

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model")
        self.autocomplete_field = kwargs.pop("autocomplete_field", "name")
        super(AutocompleteListField, self).__init__(*args, **kwargs)
        self.widget.model = self.model
        self.widget.autocomplete_field = self.autocomplete_field 

    def prepare_value(self, value):
        if not value:
            return []
        if isinstance(value, list):
            values = []
            for v in value:
                if isinstance(v, int):
                    values.append(getattr(self.model.objects.get(id=v), self.autocomplete_field))
                else:
                    values.append(v)
            return values
        return list(value.values_list(self.autocomplete_field, flat=True))

    def to_python(self, value):
        values = sorted(set([v.strip() for v in value if v.strip()]))
        return [{self.autocomplete_field: v} for v in values]