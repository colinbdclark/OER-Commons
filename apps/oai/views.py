from django.core.exceptions import ImproperlyConfigured


def oai(request, repository=None):

    if repository is None:
        raise ImproperlyConfigured()

    return repository.process(request)
