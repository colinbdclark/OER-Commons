from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from oai.exceptions import InvalidMetadataPrefix


class Header(object):

    def __init__(self, identifier, datestamp, sets=[]):
        self.identifier = identifier
        self.datestamp = datestamp
        self.sets = sets

    def render(self):
        return mark_safe(render_to_string("oai/header.xml", dict(header=self)))

    def __unicode__(self):
        return self.render()


class Record(object):

    def __init__(self, header, metadata):
        self.header = header
        self.metadata = metadata

    def render(self):
        return mark_safe(render_to_string("oai/record.xml", dict(header=self.header, metadata=self.metadata)))

    def __unicode__(self):
        return self.render()


class MetadataFormat(object):

    BATCH_SIZE = 100
    schema = None
    namespace = None

    def __init__(self, repository):
        self.repository = repository

    def build_header(self, item):
        raise NotImplementedError()

    def build_metadata(self, item, site):
        raise NotImplementedError()

    def get_items(self, from_date=None, until_date=None, set=None):
        raise NotImplementedError()

    def get_item(self, identifier):
        raise NotImplementedError()

    def supported_by(self, item):
        raise NotImplementedError()

    def list_identifiers(self, page_number=1, from_date=None, until_date=None, set=None):
        headers = []
        items = Paginator(self.get_items(from_date, until_date, set), self.BATCH_SIZE).page(page_number)
        for item in items.object_list:
            header = self.repository.build_header(item)
            headers.append(header)
        next_page_number = None
        if items.has_next():
            next_page_number = items.next_page_number()
        return headers, next_page_number, items.paginator.count

    def list_records(self, page_number=1, from_date=None, until_date=None, set=None):
        records = []
        items = Paginator(self.get_items(from_date, until_date, set), self.BATCH_SIZE).page(page_number)
        site = Site.objects.get_current()
        for item in items.object_list:
            header = self.repository.build_header(item)
            metadata = self.build_metadata(item, site)
            records.append(Record(header, metadata))
        next_page_number = None
        if items.has_next():
            next_page_number = items.next_page_number()
        return records, next_page_number, items.paginator.count

    def get_record(self, identifier):
        item = self.repository.get_item(identifier)
        if not self.supported_by(item):
            raise InvalidMetadataPrefix(u"The value of the metadataPrefix argument is not supported by the item identified by the value of the identifier argument.")
        site = Site.objects.get_current()
        return Record(self.repository.build_header(item), self.build_metadata(item, site))
