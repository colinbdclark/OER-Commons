from django.core.paginator import EmptyPage
from django.template.loader import render_to_string
from oai import DATETIME_FORMAT
from oai.exceptions import BadArgument, InvalidMetadataPrefix, NoRecordsMatch, \
    NoSetHierarchy, NoMetadataFormats
import cjson
import datetime


IDENTIFIER = "identifier"
METADATA_PREFIX = "metadataPrefix"
RESUMPTION_TOKEN = "resumptionToken"
SET = "set"
FROM = "from"
UNTIL = "until"


class Verb(object):

    def __init__(self, repository, request):
        self.repository = repository
        self.request = request
        self.raw_arguments = {}
        self.parse_arguments()

    def parse_arguments(self):
        pass

    def get_response(self):
        raise NotImplementedError()


class Identify(Verb):

    def get_response(self):
        return render_to_string("oai/identify.xml",
                                dict(repository=self.repository))


class ListIdentifiers(Verb):

    def parse_arguments(self):

        resumption_token = self.request.REQUEST.get(RESUMPTION_TOKEN, None)
        if resumption_token:
            self.raw_arguments[RESUMPTION_TOKEN] = resumption_token
            try:
                resumption_token = cjson.decode(resumption_token)
            except cjson.DecodeError:
                raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
            metadata_prefix = resumption_token.get(METADATA_PREFIX, None)
            from_date = resumption_token.get(FROM, None)
            until_date = resumption_token.get(UNTIL, None)
            set = resumption_token.get(SET, None)
            try:
                page = int(resumption_token["page"])
            except (KeyError, ValueError):
                raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
        else:
            metadata_prefix = self.request.REQUEST.get(METADATA_PREFIX, None)
            if metadata_prefix:
                self.raw_arguments[METADATA_PREFIX] = metadata_prefix
            from_date = self.request.REQUEST.get(FROM, None)
            if from_date:
                self.raw_arguments[FROM] = from_date
            until_date = self.request.REQUEST.get(UNTIL, None)
            if until_date:
                self.raw_arguments[UNTIL] = until_date
            set = self.request.REQUEST.get(SET, None)
            if set:
                self.raw_arguments[SET] = set
            page = 1

        self.page = page

        if not metadata_prefix:
            if resumption_token:
                raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
            else:
                raise BadArgument(u"%s is required" % METADATA_PREFIX)
        metadata_format = self.repository.metadata_formats.get(metadata_prefix)
        if not metadata_format:
            if resumption_token:
                raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
            else:
                raise InvalidMetadataPrefix(u"Specified %s is not supported by this repository" % METADATA_PREFIX)
        self.metadata_prefix = metadata_prefix
        self.metadata_format = metadata_format

        if from_date is not None:
            try:
                from_date = datetime.datetime.strptime(from_date, DATETIME_FORMAT)
            except ValueError:
                if resumption_token:
                    raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
                else:
                    raise BadArgument(u"Invalid date format in %s argument" % FROM)
        self.from_date = from_date

        if until_date is not None:
            try:
                until_date = datetime.datetime.strptime(until_date, DATETIME_FORMAT)
            except ValueError:
                if resumption_token:
                    raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
                else:
                    raise BadArgument(u"Invalid date format in %s argument" % UNTIL)
        self.until_date = until_date

        if set is not None:
            try:
                sets = self.repository.list_sets()
            except NoSetHierarchy:
                if resumption_token:
                    raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
                else:
                    raise

            if set not in [s.spec for s in sets]:
                if resumption_token:
                    raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
                else:
                    raise BadArgument(u"Specified %s does not exist in this repository" % SET)
        self.set = set

    def build_resumption_token(self, next_page_number):
        resumption_token = {"page": next_page_number}
        resumption_token[METADATA_PREFIX] = self.metadata_prefix
        if self.from_date:
            resumption_token[FROM] = self.from_date.strftime(DATETIME_FORMAT)
        if self.until_date:
            resumption_token[UNTIL] = self.until_date.strftime(DATETIME_FORMAT)
        if self.set:
            resumption_token[SET] = self.set
        return cjson.encode(resumption_token)

    def get_response(self):
        try:
            headers, next_page_number, total_items = self.metadata_format.list_identifiers(self.page, self.from_date, self.until_date, self.set)
        except EmptyPage:
            raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
        if not headers:
            raise NoRecordsMatch(u"No records match this request")
        if next_page_number:
            resumption_token = self.build_resumption_token(next_page_number)
        else:
            resumption_token = None
        return render_to_string("oai/list-identifiers.xml",
                                  dict(headers=headers,
                                       resumption_token=resumption_token,
                                       total_items=total_items))


class ListRecords(ListIdentifiers):

    def get_response(self):
        try:
            records, next_page_number, total_items = self.metadata_format.list_records(self.page, self.from_date, self.until_date, self.set)
        except EmptyPage:
            raise BadArgument(u"Invalid %s" % RESUMPTION_TOKEN)
        if not records:
            raise NoRecordsMatch(u"No records match this request")
        if next_page_number:
            resumption_token = self.build_resumption_token(next_page_number)
        else:
            resumption_token = None
        return render_to_string("oai/list-records.xml",
                                  dict(records=records,
                                       resumption_token=resumption_token,
                                       total_items=total_items))


class GetRecord(Verb):

    def parse_arguments(self):

        metadata_prefix = self.request.REQUEST.get(METADATA_PREFIX, None)

        if not metadata_prefix:
            raise BadArgument(u"%s is required" % METADATA_PREFIX)
        self.raw_arguments[METADATA_PREFIX] = metadata_prefix
        metadata_format = self.repository.metadata_formats.get(metadata_prefix)
        if not metadata_format:
            raise InvalidMetadataPrefix(u"Specified %s is not supported by this repository" % METADATA_PREFIX)
        self.metadata_prefix = metadata_prefix
        self.metadata_format = metadata_format

        identifier = self.request.REQUEST.get(IDENTIFIER, None)
        if not identifier:
            raise BadArgument(u"%s is required" % IDENTIFIER)
        self.raw_arguments[IDENTIFIER] = identifier
        self.identifier = identifier

    def get_response(self):
        record = self.metadata_format.get_record(self.identifier)
        return render_to_string("oai/get-record.xml",
                                  dict(record=record))


class ListMetadataFormats(Verb):

    def parse_arguments(self):

        identifier = self.request.REQUEST.get(IDENTIFIER, None)
        if identifier:
            self.raw_arguments[IDENTIFIER] = identifier
        self.identifier = identifier

    def get_response(self):
        metadata_formats = []
        if not self.identifier:
            metadata_formats = self.repository.metadata_formats.items()
        else:
            for prefix, format in self.repository.metadata_formats.items():
                try:
                    format.get_record(self.identifier)
                except InvalidMetadataPrefix:
                    continue
                metadata_formats.append((prefix, format))
            if not metadata_formats:
                raise NoMetadataFormats(u"There are no metadata formats available for the specified item.")
        return render_to_string("oai/list-metadata-formats.xml",
                                dict(metadata_formats=metadata_formats))


class ListSets(Verb):

    def get_response(self):
        sets = self.repository.list_sets()
        return render_to_string("oai/list-sets.xml", dict(sets=sets))
