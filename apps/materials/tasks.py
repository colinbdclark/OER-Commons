from celery.decorators import task
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
