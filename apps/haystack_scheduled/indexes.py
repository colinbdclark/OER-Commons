from django.db import models
from django.utils.encoding import smart_str
from haystack.indexes import SearchIndex
from haystack.query import SearchQuerySet


class ScheduledSearchIndex(SearchIndex):

    indexed_field = "is_indexed"

    #noinspection PyUnusedLocal
    def mark_for_reindexing(self, instance, **kwargs):
        is_indexed = getattr(instance, self.indexed_field)
        if is_indexed:
            self.model.objects.filter(pk=instance.pk).update(**{self.indexed_field: False})

    def _setup_save(self, model):
        models.signals.post_save.connect(self.mark_for_reindexing, sender=model)
        models.signals.m2m_changed.connect(self.mark_for_reindexing, sender=model)

    def _setup_delete(self, model):
        models.signals.post_delete.connect(self.remove_object, sender=model)

    def _teardown_save(self, model):
        models.signals.post_save.disconnect(self.mark_for_reindexing, sender=model)
        models.signals.m2m_changed.disconnect(self.mark_for_reindexing, sender=model)

    def _teardown_delete(self, model):
        models.signals.post_delete.disconnect(self.remove_object, sender=model)

    def should_update(self, instance, **kwargs):
        return getattr(instance, self.indexed_field)

    def update_object(self, instance, **kwargs):
        if self.should_update(instance, **kwargs):
            self.model.objects.filter(pk=instance.pk).update(**{self.indexed_field: True})
            self.backend.update(self, [instance])

    def get_queryset(self):
        return self.index_queryset()

    def index_queryset(self):
        qs = self.model._default_manager.all()
        return qs.filter(**{self.indexed_field: False})

    def clear(self):
        self.model.objects.all().update(**{self.indexed_field: False})
        super(ScheduledSearchIndex, self).clear()

    def update(self):
        items = self.index_queryset()
        items.update(**{self.indexed_field: True})
        self.backend.update(self, items)

    def full_prepare(self, obj):
        data = super(ScheduledSearchIndex, self).full_prepare(obj)

        # This is the only place where we can set is_indexed=True if
        # indexing was initiated from management command.
        if not getattr(obj, self.indexed_field):
            obj.__class__.objects.update(**{self.indexed_field: True})

        return data


class Indexed(models.Model):

    is_indexed = models.BooleanField(default=False, db_index=True)

    def reindex(self):
        from haystack import site
        index = site.get_index(self.__class__)
        if isinstance(index, ScheduledSearchIndex):
            index.mark_for_reindexing(self)

    class Meta:
        abstract = True
