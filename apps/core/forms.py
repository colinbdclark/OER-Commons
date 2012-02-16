# coding: utf-8
from django import forms
from django.core.urlresolvers import reverse
from django.core.validators import EMPTY_VALUES
from django.template.loader import render_to_string
import string


class AutoCreateField(forms.Field):

    widget = forms.TextInput
    hidden_widget = forms.HiddenInput

    def __init__(self, to_field_name, **kwargs):
        self.to_field_name = to_field_name
        super(AutoCreateField, self).__init__(**kwargs)

    def prepare_value(self, value):
        if hasattr(value, '_meta'):
            return value.serializable_value(self.to_field_name)
        return super(AutoCreateField, self).prepare_value(value)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        return {self.to_field_name: value}


class MultipleAutoCreateWidgetMixin(object):

    default_separator = u","

    def __init__(self, separator=None, *args, **kwargs):
        self.separator = separator or self.default_separator
        #noinspection PyArgumentList
        super(MultipleAutoCreateWidgetMixin, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        #noinspection PyUnresolvedReferences
        value = super(MultipleAutoCreateWidgetMixin, self).value_from_datadict(data, files, name)
        return filter(None, map(string.strip, value.split(self.separator)))

    def render(self, name, value, attrs=None):
        if hasattr(value, '__iter__'):
            value = self.separator.join(value)
        #noinspection PyUnresolvedReferences
        return super(MultipleAutoCreateWidgetMixin, self).render(name, value, attrs)



class MultipleAutoCreateInput(MultipleAutoCreateWidgetMixin, forms.TextInput):
    pass


class MultipleAutoCreateHiddenInput(MultipleAutoCreateWidgetMixin, forms.HiddenInput):
    pass


class MultipleAutoCreateTextarea(MultipleAutoCreateWidgetMixin, forms.Textarea):
    default_separator = u"\n"


class MultipleAutoCreateField(AutoCreateField):

    widget = MultipleAutoCreateInput
    hidden_widget = MultipleAutoCreateHiddenInput

    def prepare_value(self, value):
        if hasattr(value, '__iter__'):
            return [super(MultipleAutoCreateField, self).prepare_value(v) for v in value]
        return super(MultipleAutoCreateField, self).prepare_value(value)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return []
        return [{self.to_field_name: v} for v in value]


class AutocompleteListWidget(MultipleAutoCreateInput):

    def __init__(self, model, field_name, *args, **kwargs):
        self.model = model
        self.field_name = field_name
        self.new_item_label = kwargs.pop("new_item_label", None)
        super(AutocompleteListWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        opts = self.model._meta
        app_label = opts.app_label
        model_name = opts.object_name.lower()
        autocomplete_url = reverse(
            "utils:autocomplete",
            args=(app_label, model_name,self.field_name)
        )
        new_item_label = self.new_item_label or u"Add new %s " % opts.verbose_name.lower()
        if value and not isinstance(value, list):
            value = [value]
        #noinspection PyUnresolvedReferences
        return render_to_string("core/include/autocomplete-list-widget.html",
                                dict(name=name, value=value, attrs=attrs,
                                     autocomplete_url=autocomplete_url,
                                     new_item_label=new_item_label))
