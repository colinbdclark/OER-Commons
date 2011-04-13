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


def process_item(_type, id, status, slug, title, collection, url, timeout):
    if url.startswith('https://'):
        return None

    row = [_type, slug, title, collection, url]

    for actual_status, reason, redirect_url in process_url(url, timeout):
        if actual_status is None:
            row.append(reason)
        else:
            row.append("%i %s" % (actual_status, reason))

        if redirect_url:
            row.append(redirect_url)

    return (id, status, actual_status, row)


class Processor(pprocess.Exchange):

    def store_data(self, ch):
        result = ch.receive()
        if result:
            id, status, actual_status, row = result
            if status != actual_status:
                _type = row[0]
                if actual_status not in self.updated_statuses:
                    self.updated_statuses[actual_status] = {}
                if _type not in self.updated_statuses[actual_status]:
                    self.updated_statuses[actual_status][_type] = []
                self.updated_statuses[actual_status][_type].append(id)
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
    processor.updated_statuses = {}

    process = processor.manage(pprocess.MakeReusable(process_item))

    for id, status, slug, title, collection, url in Course.objects.values_list(
                                  "id", "http_status", "slug", "title", "collection", "url"):
        process("course", id, status, slug, title,
                get_name_from_id(Collection, collection), url, timeout)

    for id, status, slug, title, collection, url in Library.objects.values_list(
                                  "id", "http_status", "slug", "title", "collection", "url"):
        process("library", id, status, slug, title,
                      get_name_from_id(Collection, collection), url, timeout)

    for id, status, slug, title, url in CommunityItem.objects.values_list(
                                  "id", "http_status", "slug", "title", "url"):
        process("community item", id, status, slug, title, "", url, timeout)

    processor.finish()

    for status, items in processor.updated_statuses.items():
        for _type, ids in items.items():
            if _type == 'course':
                model = Course
            elif _type == 'library':
                model = Library
            elif _type == 'community item':
                model = CommunityItem
            else:
                continue
            print "Set %s status for %i %s" % (str(status), len(items), unicode(model._meta.verbose_name_plural))
            model.objects.filter(id__in=ids).update(http_status=status)

    filename = '%s-%s.csv' % (CHECK_URLS, datetime.datetime.now().isoformat())
    report = Report(type=CHECK_URLS)
    report.file.save(filename, File(f))

    f.close()

    print "Done!"

