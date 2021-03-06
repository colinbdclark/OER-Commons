from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.http import Http404
from django.views.generic.simple import direct_to_template
from oai.exceptions import OAIError, NoSetHierarchy, IdDoesNotExist
from oai.metadata import Header
from oai.verbs import Identify, ListIdentifiers, ListRecords, GetRecord, \
    ListMetadataFormats, ListSets
import datetime


class Repository(object):

    verbs = {
        "Identify": Identify,
        "ListIdentifiers": ListIdentifiers,
        "ListRecords": ListRecords,
        "GetRecord": GetRecord,
        "ListMetadataFormats": ListMetadataFormats,
        "ListSets": ListSets,
    }

    def __init__(self, name, identifier, metadata_formats, admin_email):
        self.name = name
        self.identifier = identifier
        self.metadata_formats = dict((key, format(self)) for key, format in metadata_formats.items())
        self.admin_email = admin_email

    def base_url(self, microsite=None):
        kwargs = {}
        if microsite:
            kwargs["microsite"] = microsite.slug
        return "http://%s%s" % (Site.objects.get_current().domain,
                                reverse("oai", kwargs=kwargs))

    @property
    def earliest_timestamp(self):
        return datetime.datetime(2000, 1, 1)

    @property
    def identifier_prefix(self):
        return "oai:%s:" % self.identifier

    @property
    def sample_identifier(self):
        header = None
        for metadata_format in self.metadata_formats:
            headers = metadata_format.list_headers(self)
            if headers:
                header = headers[0]
        if header is None:
            return None
        return header.identifier

    def list_sets(self, microsite):
        raise NoSetHierarchy(u"Sets are not supported by this repository")

    def get_item(self, identifier, microsite=None):
        if not identifier.startswith(self.identifier_prefix):
            raise IdDoesNotExist(u"Invalid identifier")

        identifier = identifier[len(self.identifier_prefix):]
        try:
            app_label, module_name, id = identifier.split(".")
            id = int(id)
        except ValueError:
            raise IdDoesNotExist(u"Invalid identifier")
        model = models.get_model(app_label, module_name)
        if model is None:
            raise IdDoesNotExist(u"Invalid identifier")
        try:
            item = model.objects.get(id=id)
        except model.DoesNotExist:
            raise IdDoesNotExist(u"Invalid identifier")
        
        if microsite and microsite not in item.microsites():
            raise IdDoesNotExist(u"Invalid identifier")
        return item

    def get_sets(self, item):
        return []

    def build_header(self, item):
        identifier = "%s%s.%s.%i" % (self.identifier_prefix,
                                     item._meta.app_label,
                                     item._meta.module_name,
                                     item.id)
        datestamp = item.published_on
        sets = self.get_sets(item)
        return Header(identifier, datestamp, sets)

    def process(self, request, microsite=None):
        verb = request.REQUEST.get("verb", None)
        handler = self.verbs.get(verb, None)
        base_url = self.base_url(microsite)
        if handler is None:
            raise Http404()
        now = datetime.datetime.now()
        try:
            handler = handler(self, request, microsite=microsite)
            response = handler.get_response()
        except OAIError as err:
            return direct_to_template(request, "oai/error.xml",
                                  dict(verb=verb, now=now, repository=self,
                                       base_url=base_url, code=err.code,
                                       message=err[0]),
                                  mimetype="text/xml")
        return direct_to_template(request, "oai/response.xml",
                                  dict(verb=verb, now=now, repository=self,
                                       base_url=base_url, response=response,
                                       arguments=handler.raw_arguments),
                                  mimetype="text/xml")
