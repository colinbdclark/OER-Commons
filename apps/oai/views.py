from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from materials.models.microsite import Microsite


def oai(request, repository=None, microsite=None):

    if repository is None:
        raise ImproperlyConfigured()

    if microsite:
        try:
            microsite = Microsite.objects.get(slug=microsite)
        except Microsite.DoesNotExist:
            raise Http404()

    return repository.process(request, microsite=microsite)
