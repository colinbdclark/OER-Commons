from cache_utils.decorators import cached
from haystack.query import SearchQuerySet
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

        kw = kw.strip()

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

        # If the keyword contains one and only one quote char we remove it
        if kw.count(u'"') == 1:
            kw = kw.replace(u'"', u'')

        if not ALL_CAPS.match(kw):
            kw = titlecase(kw)

        cleaned_keywords.add(kw)

    return sorted(cleaned_keywords)


@cached(60 * 60 * 24)
def get_name_from_id(model, id):
    """
    Lookup a model instance by id and return its name. Return None if an object
    with given id does not exist.
    """
    results = model.objects.filter(id=id).values_list("name", flat=True).order_by()
    if results:
        return results[0]
    return None


@cached(60 * 60 * 24)
def get_slug_from_id(model, id):
    """
    Lookup a model instance by id and return its slug. Return None if an object
    with given id does not exist.
    """
    results = model.objects.filter(id=id).values_list("slug", flat=True).order_by()
    if results:
        return results[0]
    return None


@cached(60 * 60 * 24)
def get_name_from_slug(model, slug):
    """
    Lookup a model instance by slug and return its name. Return None if an object
    with given slug does not exist.
    """
    results = model.objects.filter(slug=slug).values_list("name", flat=True).order_by()
    if results:
        return results[0]
    return None


def get_facets_for_field(field, model=None, facet_limit=None, facet_mincount=None):

    query = SearchQuerySet()
    if model is not None:
        if isinstance(model, (tuple, list)):
            query = query.models(*model)
        else:
            query = query.models(model)
    query = query.narrow("is_displayed:true")
    query = query.facet(field)
    if facet_limit:
        query = query.facet_limit(facet_limit)
    if facet_mincount:
        query = query.facet_mincount(facet_mincount)
    return query.facet_counts().get("fields", {}).get(field, [])


def first_neighbours_last(pages, current_page_idx, nb_left, nb_right):
    sublist = []
    # setup some batches and indexes
    firstIdx = 0
    lastIdx = len(pages) - 1
    assert(current_page_idx >= 0 and current_page_idx <= lastIdx)
    assert(nb_left >= 0 and nb_right >= 0)
    prevIdx = current_page_idx - nb_left
    nextIdx = current_page_idx + 1
    firstBatch = pages[0]
    lastBatch = pages[len(pages) - 1]

    # add first batch
    if firstIdx < current_page_idx:
        sublist.append(firstBatch)

    # there must probably be space
    if firstIdx + 1 < prevIdx:
        # we skip batches between first batch and first previous batch
        sublist.append(None)

    # add previous batches
    for i in range(prevIdx, prevIdx + nb_left):
        if firstIdx < i:
            # append previous batches
            sublist.append(pages[i])

    # add current batch
    sublist.append(pages[current_page_idx])

    # add next batches
    for i in range(nextIdx, nextIdx + nb_right):
        if i < lastIdx:
            # append previous batch
            sublist.append(pages[i])

    # there must probably be space
    if nextIdx + nb_right < lastIdx:
        # we skip batches between last batch and last next batch
        sublist.append(None)

    # add last batch
    if current_page_idx < lastIdx:
        sublist.append(lastBatch)
    return sublist
