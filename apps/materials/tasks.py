from __future__ import absolute_import

from celery.decorators import task
from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor
from haystack_scheduled.indexes import Indexed
from sorl.thumbnail.shortcuts import delete
from utils import update_item
import httplib
import logging
import os
import sys
import urllib
import urllib2


@task
def reindex_microsite_topic(topic):
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
        if isinstance(instance, Indexed):
            instance.reindex()


class TimeoutError(Exception):

    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


def timeout(function=None, timeout_duration=10, default=None):

    def raise_timeout(signum, frame):
        raise TimeoutError()

    def wrapper(func):

        def wrapped(*args, **kwargs):
            import signal
            signal.signal(signal.SIGALRM, raise_timeout)
            signal.alarm(timeout_duration)
            try:
                return func(*args, **kwargs)
            except TimeoutError:
                return default
            finally:
                signal.alarm(0)

        return wrapped

    if function:
        return wrapper(function)

    return wrapper


check_url_logger = logging.getLogger("oercommons.check_urls")


def get_url_status_code(url):
    url = url.strip()
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    if not url:
        return

    check_url_logger.info(u"Check URL status for '%s'" % url)

    try:
        host = url.split('/')[2]
        path = "/" + "/".join(url.split('/')[3:])
    except:
        check_url_logger.error(u"Invalid URL '%s'" % url)
        return None

    @timeout(timeout_duration=60)
    def get_status(host, path):
        try:
            conn = httplib.HTTPConnection(host)
            conn.request("HEAD", path)
            response = conn.getresponse()
            return response.status
        except TimeoutError:
            check_url_logger.error(u"Timeout error '%s'" % url)
            raise
        except:
            check_url_logger.error(u"'%s' %s %s" % (url, sys.exc_info()[0], sys.exc_info()[1]))
            return None

    status_code = get_status(host, path)

    if status_code is not None:
        check_url_logger.info(u"Response code for '%s' is %i" % (url, status_code))
    else:
        check_url_logger.error(u"Can't get response code code for '%s'" % url)

    return status_code


def check_url_status(item):
    status_code = get_url_status_code(item.url)

    if item.http_status != status_code:
        update_item(item, http_status=status_code)
        if isinstance(item, Indexed):
            item.reindex()



screenshot_logger = logging.getLogger("oercommons.screenshots")


def update_screenshot(item, force=False):

    api_key = getattr(settings, "URL2PNG_KEY", None)
    api_secret = getattr(settings, "URL2PNG_SECRET", None)
    if not api_key or not api_secret:
        screenshot_logger.warning(u"Either URL2PNG_KEY or URL2PNG_SECRET is missing. Can't fetch screenshot.")
        return

    url = item.url

    url = url.strip()
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    if not url:
        return

    if item.http_status != 200:
        screenshot_logger.warning(u"Skipping '%s'. HTTP status is not 200." % item.url)
        return

    if item.screenshot and not force:
        screenshot_logger.warning(u"Skipping '%s'. Screenshot exists already." % item.url)
        return

    url_hash = md5_constructor(smart_str(url)).hexdigest()
    filename = "%s-%i-%s.png" % (item._meta.object_name.lower(), item.id, url_hash)
    filename = os.path.join(item.screenshot.field.get_directory_name(), filename)

    # Remove existing screenshot
    if item.screenshot:
        try:
            delete(item.screenshot)
        except OSError:
            pass
        update_item(item, screenshot=None)

    full_path = os.path.join(settings.MEDIA_ROOT, filename)
    dirname = os.path.dirname(full_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    bounds = "1000x1000"
    token = md5_constructor("%s+%s" % (api_secret, url)).hexdigest()
    screenshot_url = "http://api.url2png.com/v3/%s/%s/%s/%s" % (api_key, token, bounds, url)

    response = urllib2.urlopen(screenshot_url, timeout=120)
    f = open(full_path, "w+")
    f.write(response.read())
    f.close()
    update_item(item, screenshot=filename)
    screenshot_logger.info(u"Fetched screenshot for '%s'" % url)

