from django.core.files.base import File
from materials.models.common import Collection
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from materials.utils import get_name_from_id
from reports.models import CHECK_URLS, Report
from tempfile import NamedTemporaryFile
import csv
import datetime
import httplib
import pprocess
import signal
import sys
import urllib


BASE_HEADER = ('TYPE', 'NAME', 'TITLE', 'COLLECTION', 'URL', 'STATUS')


class TimeoutError(Exception):
    def __init__(self, value="Timed Out"):
        self.value = value
    def __str__(self):
        return repr(self.value)


def process_url(url, timeout, statuses=None):

    if statuses is None:
        statuses = list()

    if len(statuses) > 6:
        return statuses

    url = url.strip()
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    if not url:
        statuses.append((None, "Invalid URL", None))
        return statuses

    try:
        host = url.split('/')[2]
        path = "/".join(url.split('/')[3:])
    except:
        statuses.append((None, "Invalid URL", None))
        return statuses

    def timeout_handler(signum, frame):
        raise TimeoutError()

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    conn = httplib.HTTPConnection(host)
    try:
        conn.request("GET", "/" + path)
        http_response = conn.getresponse()
    except:
        statuses.append((None, sys.exc_info()[1], None))
        return statuses
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        conn.close()

    signal.alarm(0)

    if http_response.status in (301, 302, 303):
        headers = http_response.getheaders()
        for header, value in headers:
            if header == 'location':
                if value.startswith('/'):
                    value = 'http://' + host + value
                statuses.append((http_response.status, http_response.reason, value))
                process_url(value, timeout, statuses=statuses)
    else:
        statuses.append((http_response.status, http_response.reason, None))

    return statuses


def process_item(_type, name, title, collection, url, timeout):
    if url.startswith('https://'):
        return None

    row = [_type, name, title, collection, url]
    delete = False

    for status, reason, redirect_url in process_url(url, timeout):
        if status is None:
            row.append(reason)
        else:
            row.append("%i %s" % (status, reason))

        if redirect_url:
            row.append(redirect_url)

        if status == 404:
            delete = True

    return (row, delete)


class Processor(pprocess.Exchange):

    def store_data(self, ch):
        result = ch.receive()
        if result:
            row, delete = result
            if delete:
                self.to_be_deleted.append((row[0], row[1]))
            row = map(lambda x: unicode(x).encode('utf-8'), row)
            self.writer.writerow(row)
        self.cnt += 1
        if self.cnt % 10 == 0:
            print "%i of %i..." % (self.cnt, self.total_items)


def process_check_urls(limit=10, timeout=30):

    f = NamedTemporaryFile()
    writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

    writer.writerow(BASE_HEADER)

    processor = Processor(limit=limit, reuse=1)
    processor.writer = writer
    processor.total_items = Course.objects.all().count() + \
                  Library.objects.all().count() + \
                  CommunityItem.objects.all().count()
    processor.cnt = 0
    processor.to_be_deleted = []

    process = processor.manage(pprocess.MakeReusable(process_item))

    for slug, title, collection, url in Course.objects.values_list("slug",
                               "title", "collection", "url"):
        process("course", slug, title,
                get_name_from_id(Collection, collection), url, timeout)

    for slug, title, collection, url in Library.objects.values_list("slug",
                               "title", "collection", "url"):
        process("library", slug, title,
                      get_name_from_id(Collection, collection), url, timeout)

    for slug, title, url in CommunityItem.objects.values_list("slug",
                               "title", "url"):
        process("community item", slug, title, "", url, timeout)

    processor.finish()

    if processor.to_be_deleted:
        print "Removing %i items with 404 status" % len(processor.to_be_deleted)
        for _type, slug in processor.to_be_deleted:
            # Remove items which have 404 status
            if _type == 'course':
                model = Course
            elif _type == 'library':
                model = Library
            elif _type == 'community item':
                model = CommunityItem
            else:
                model = None
            if model:
                try:
                    model.objects.get(slug=slug).delete()
                except model.DoesNotExist:
                    pass

    filename = '%s-%s.csv' % (CHECK_URLS, datetime.datetime.now().isoformat())
    report = Report(type=CHECK_URLS)
    report.file.save(filename, File(f))

    f.close()

    print "Done!"

