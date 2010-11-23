from cache_utils.decorators import cached
from haystack.query import SearchQuerySet
from materials.models.material import PUBLISHED_STATE
from titlecase import titlecase, ALL_CAPS
import re


ALPHANUM_RE = re.compile(r"\w+", re.IGNORECASE | re.UNICODE)


def cleanup_keywords(keywords):
    """
    Normalize the keywords: convert to titlecase, strip whitespace, split if
    necessary, remove duplicates, remove empty strings, sort.
    """

    cleaned_keywords = set()
    for kw in keywords:

        if not ALPHANUM_RE.match(kw):
            continue

        # If the keyword contains commas or semicolons we split it and
        # re-process 
        if u";" in kw:
            cleaned_keywords.update(cleanup_keywords(kw.split(u";")))
            continue
        if u"," in kw:
            cleaned_keywords.update(cleanup_keywords(kw.split(u",")))
            continue
        if u"|" in kw:
            cleaned_keywords.update(cleanup_keywords(kw.split(u"|")))
            continue

        kw = kw.strip()

        # If the keyword contains one and only one quote char we remove it
        if kw.count(u'"') == 1:
            kw = kw.replace(u'"', u'')

        if not ALL_CAPS.match(kw):
            kw = titlecase(kw)

        cleaned_keywords.add(kw)

    return sorted(cleaned_keywords)


@cached(60 * 60 * 24)
def get_name_from_slug(model, slug):
    """
    Lookup a model instance by slug and return its name. Use caching to reduce
    the number of database queries. Return None if an object with given slug
    does not exist.
    """
    result = model.objects.filter(slug=slug)
    if not result.count():
        return None
    return result[0].name


@cached(60 * 60 * 24)
def get_name_from_id(model, id):
    """
    Lookup a model instance by id and return its name. Use caching to reduce
    the number of database queries. Return None if an object with given id
    does not exist.
    """
    try:
        return model.objects.get(pk=1).name
    except model.DoesNotExist:
        return None


def get_facets_for_field(field, model=None):

    query = SearchQuerySet()
    if model is not None:
        query = query.models(model)
    query = query.filter(workflow_state=PUBLISHED_STATE)
    query = query.facet(field)
    return query.facet_counts()["fields"][field]
