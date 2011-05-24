from celery.decorators import task
from haystack.query import SearchQuerySet
import requests
import urllib


@task
def check_url_status(item):
    from haystack.sites import site

    url = item.url
    url = url.strip()
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    if not url:
        return

    try:
        response = requests.get(url)
        status_code = response.status_code
    except:
        return

    model = item.__class__

    if item.http_status != status_code:
        model.objects.filter(id=item.id).update(http_status=status_code)
        item = model.objects.get(id=item.id)
        site.update_object(item)


@task
def reindex_microsite_topic(topic):
    from haystack.sites import site
    
    # get all objects from this topic and all objects with this topic's keywords
    query = "topics:%s" % topic.id
    topic_keywords = topic.keywords.values_list("slug", flat=True)
    microsite_keywords = topic.microsite.keywords.values_list("slug", flat=True)
    if topic_keywords and microsite_keywords:
        query = "%s OR ((%s) AND (%s))" % (query,
                                           " OR ".join(["keywords:%s" % kw for kw in topic_keywords]),
                                           " OR ".join(["keywords:%s" % kw for kw in microsite_keywords]),)

    print query

    for result in SearchQuerySet().narrow(query).load_all():
        instance = result.object
        site.update_object(instance)
        