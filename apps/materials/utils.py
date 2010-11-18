from django.core.cache import cache


def get_name_from_slug(model, slug):
    """
    Lookup a model instance by slug and return its name. Use caching to reduce
    the number of database queries. Return None if an object with given slug
    does not exist.
    """
    key = "get_name_from_slug_cached_dict"
    cached_dict = cache.get(key, None)
    if cached_dict is None:
        cached_dict = dict(model.objects.all().values_list("slug", "name"))
        cache.set(key, cached_dict)

    if slug in cached_dict:
        return cached_dict[slug]

    result = model.objects.filter(slug=slug)
    if not result.count():
        return None
    name = result[0].name
    cached_dict[slug] = name
    cache.set(key, cached_dict)
    return name

