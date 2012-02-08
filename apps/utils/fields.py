from django.db import models
from south.modelsinspector import add_introspection_rules


class AutoCreateForeignKey(models.ForeignKey):

    def __init__(self, *args, **kwargs):
        self.respect_all_fields = kwargs.pop("respect_all_fields", False)
        super(AutoCreateForeignKey, self).__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        if isinstance(data, dict):
            to = self.rel.to
            if self.respect_all_fields:
                for field in to._meta.fields:
                    if field.name not in data:
                        if field.default == models.NOT_PROVIDED:
                            data[field.name] = None
                        else:
                            data[field.name] = field.default
            data = to.objects.get_or_create(**data)[0]
        super(AutoCreateForeignKey, self).save_form_data(instance, data)

    def value_from_object(self, obj):
        "Returns the value of this field in the given model instance."
        pk = getattr(obj, self.attname)
        if pk is None:
            return
        return self.rel.to.objects.get(pk=pk)


add_introspection_rules([], ["^utils\.fields\.AutoCreateForeignKey"])


class AutoCreateManyToManyField(models.ManyToManyField):

    def __init__(self, *args, **kwargs):
        self.respect_all_fields = kwargs.pop("respect_all_fields", False)
        super(AutoCreateManyToManyField, self).__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        if isinstance(data, list):
            to = self.rel.to
            for i, value in enumerate(data):
                if isinstance(value, dict):
                    if self.respect_all_fields:
                        for field in to._meta.fields:
                            if field.name not in value:
                                if field.default == models.NOT_PROVIDED:
                                    value[field.name] = None
                                else:
                                    value[field.name] = field.default
                    data[i] = to.objects.get_or_create(**value)[0]
        super(AutoCreateManyToManyField, self).save_form_data(instance, data)


add_introspection_rules([], ["^utils\.fields\.AutoCreateManyToManyField"])


