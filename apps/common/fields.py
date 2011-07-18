from django.db import models
from django.utils.encoding import smart_unicode
from south.modelsinspector import add_introspection_rules


class SeparatedValuesField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = unicode(kwargs.pop('token', '|'))
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        if not value:
            return []
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_prep_value(self, value):
        if isinstance(value, (list, tuple)):
            value = self.token.join(map(smart_unicode, value))
        return super(SeparatedValuesField, self).get_prep_value(value)

add_introspection_rules([], ["^common\.fields\.SeparatedValuesField"])