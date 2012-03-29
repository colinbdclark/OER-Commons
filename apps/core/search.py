from celery_haystack.indexes import CelerySearchIndex
from django.db.models import signals
from haystack.exceptions import NotRegistered
from haystack.sites import site


class SearchIndex(CelerySearchIndex):

    def _setup_save(self, model=None):
        model = self.handle_model(model)
        signals.post_save.connect(self.enqueue_save, sender=model)
        signals.m2m_changed.connect(self.enqueue_save, sender=model)

    def _teardown_save(self, model=None):
        model = self.handle_model(model)
        signals.post_save.disconnect(self.enqueue_save, sender=model)
        signals.m2m_changed.disconnect(self.enqueue_save, sender=model)

    def enqueue(self, action, instance):
        if getattr(instance, "skip_indexing", False):
            return
        super(SearchIndex, self).enqueue(action, instance)


def reindex(instance):
    try:
        index = site.get_index(instance.__class__)
    except NotRegistered:
        return
    if isinstance(index, SearchIndex):
        res = index.enqueue_save(instance)
