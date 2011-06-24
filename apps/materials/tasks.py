from celery.decorators import task
from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor
from sorl.thumbnail.shortcuts import delete
import os
import shlex
import subprocess
import sys
import signal
import urllib
import httplib


@task
def reindex_microsite_topic(topic):
    from haystack.sites import site
    from haystack.query import SearchQuerySet

    objects = set()
    
    # get all objects from this topic and all objects with this topic's keywords
    query = "indexed_topics:%s" % topic.id
    for result in SearchQuerySet().narrow(query).load_all():
        objects.add(result.object)
    
    topic_keywords = topic.keywords.values_list("slug", flat=True)
    microsite_keywords = topic.microsite.keywords.values_list("slug", flat=True)
    if topic_keywords and microsite_keywords:
        query = SearchQuerySet()
        query = query.narrow("keywords(%s)" % " OR ".join(["%s" % kw for kw in topic_keywords]))
        query = query.narrow("keywords(%s)" % " OR ".join(["%s" % kw for kw in microsite_keywords]))
        for result in query.load_all():
            objects.add(result.object)

    for instance in objects:
        site.update_object(instance)


class TimeoutError(Exception):
    def __init__(self, value="Timed Out"):
        self.value = value
    def __str__(self):
        return repr(self.value)


def get_url_status_code(url):
    url = url.strip()
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    if not url:
        return

    try:
        host = url.split('/')[2]
        path = "/".join(url.split('/')[3:])
    except:
        return None

    def timeout_handler(signum, frame):
        raise TimeoutError()

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    timeout = 60
    signal.alarm(timeout)

    conn = httplib.HTTPConnection(host)
    try:
        conn.request("GET", "/" + path)
        http_response = conn.getresponse()
        status_code = http_response.status
    except:
        status_code = None
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        conn.close()

    signal.alarm(0)

    return status_code


def check_url_status(item):
    from haystack.sites import site

    status_code = get_url_status_code(item.url)

    if item.http_status != status_code:
        item.http_status = status_code
        item.save()
        site.update_object(item)


def update_screenshot(item):
    url = item.url

    url = url.strip()
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    if not url:
        return

    if item.http_status != 200:
        if item.screenshot:
            delete(item.screenshot)
            item.screenshot = None
            item.save()
        return

    url_hash = md5_constructor(smart_str(url)).hexdigest()
    filename = "%s-%i-%s.png" % (item._meta.object_name.lower(), item.id, url_hash)
    filename = os.path.join(item.screenshot.field.get_directory_name(), filename)
    if item.screenshot:
        try:
            # check that the file actually exists
            item.screenshot.size
            if item.screenshot.name == filename:
                return
            else:
                delete(item.screenshot)
                item.screenshot = None
                item.save()
        except OSError:
            pass

    full_path = os.path.join(settings.MEDIA_ROOT, filename)
    dirname = os.path.dirname(full_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    width = 1024
    height = 768

    executable = settings.WEBKIT2PNG_EXECUTABLE % dict(filename=full_path,
                                                       url='"%s"' % url.replace('"', '\\"'),
                                                       width=width,
                                                       height=height)
    if isinstance(executable, unicode):
        executable = executable.encode(sys.getfilesystemencoding())
    args = shlex.split(executable)
    subprocess.call(args)
    if os.path.exists(full_path):
        item.screenshot = filename
        item.save()
    else:
        item.screenshot = None
        item.save()


@task
def material_post_save_task(item):

    # URL has changed
    if item.var_cache.get("url") != item.url:
        check_url_status(item)

    update_screenshot(item)