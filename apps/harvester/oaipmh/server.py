from lxml.etree import ElementTree, Element, SubElement
from lxml import etree
from datetime import datetime
from urllib import urlencode
import sys, cgi

from harvester.oaipmh import common, metadata, validation, error
from harvester.oaipmh.datestamp import datestamp_to_datetime, datetime_to_datestamp

NS_OAIPMH = 'http://www.openarchives.org/OAI/2.0/'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS_OAIDC = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
NS_DC = "http://purl.org/dc/elements/1.1/"

nsmap = {
    None: NS_OAIPMH,
    'xsi': NS_XSI,
    'oai_dc': NS_OAIDC,
    'dc': NS_DC
    }

class XMLTreeServer:
    """A server that responds to messages by returning XML trees.

    This is an implementation class that normally would not be exposed
    to the outside world.

    Takes an object conforming to the OAIPMH API.
    """
    def __init__(self, server, metadata_registry, resumption_batch_size=10):
        self._server = Resumption(server, resumption_batch_size)
        self._metadata_registry = (
            metadata_registry or metadata.global_metadata_registry)
        
    def getRecord(self, **kw):
        envelope, e_getRecord = self._outputEnvelope(
            verb='GetRecord', **kw)
        record = self._server.getRecord(**kw)
        header, metadata, about = self._server.getRecord(**kw)
        e_record = SubElement(e_getRecord, nsoai('record'))
        self._outputHeader(e_record, header)   
        if not header.isDeleted():
            self._outputMetadata(e_record, kw['metadataPrefix'], metadata)
        return envelope
    
    def identify(self):
        envelope, e_identify = self._outputEnvelope(verb='Identify')
        identify = self._server.identify()
        e_repositoryName = SubElement(e_identify, nsoai('repositoryName'))
        e_repositoryName.text = identify.repositoryName()
        e_baseURL = SubElement(e_identify, nsoai('baseURL'))
        e_baseURL.text = identify.baseURL()
        e_protocolVersion = SubElement(e_identify, nsoai('protocolVersion'))
        e_protocolVersion.text = identify.protocolVersion()
        for adminEmail in identify.adminEmails():
            e = SubElement(e_identify, nsoai('adminEmail'))
            e.text = adminEmail
        e_earliestDatestamp = SubElement(e_identify,
                                         nsoai('earliestDatestamp'))
        e_earliestDatestamp.text = datetime_to_datestamp(
            identify.earliestDatestamp())
        e_deletedRecord = SubElement(e_identify,
                                     nsoai('deletedRecord'))
        e_deletedRecord.text = identify.deletedRecord()
        e_granularity = SubElement(e_identify, nsoai('granularity'))
        e_granularity.text = identify.granularity()
        compressions = identify.compression()
        if compressions != ['identity']:
            for compression in compressions:
                e_compression = SubElement(e_identify, nsoai('compression'))
                e_compression.text = compression
        return envelope

    def listMetadataFormats(self, **kw):
        envelope, e_listMetadataFormats = self._outputEnvelope(
            verb="ListMetadataFormats", **kw)
        for (metadataPrefix, schema,
             metadataNamespace) in self._server.listMetadataFormats(**kw):
            e_metadataFormat = SubElement(e_listMetadataFormats,
                                          nsoai('metadataFormat'))
            e_metadataPrefix = SubElement(e_metadataFormat,
                                          nsoai('metadataPrefix'))
            e_metadataPrefix.text = metadataPrefix
            e_schema = SubElement(e_metadataFormat,
                                  nsoai('schema'))
            e_schema.text = schema
            e_metadataNamespace = SubElement(e_metadataFormat,
                                             nsoai('metadataNamespace'))
            e_metadataNamespace.text = metadataNamespace
        return envelope            

    def listIdentifiers(self, **kw):
        envelope, e_listIdentifiers = self._outputEnvelope(
            verb='ListIdentifiers', **kw)
        def outputFunc(element, headers, token_kw):
            for header in headers:
                self._outputHeader(element, header)
        self._outputResuming(
            e_listIdentifiers,
            self._server.listIdentifiers,
            outputFunc,
            kw)
        return envelope
    
    def listRecords(self, **kw):
        envelope, e_listRecords = self._outputEnvelope(
            verb="ListRecords", **kw)
        def outputFunc(element, records, token_kw):
            metadataPrefix = token_kw['metadataPrefix']
            for header, metadata, about in records:
                e_record = SubElement(e_listRecords, nsoai('record'))
                self._outputHeader(e_record, header)
                if not header.isDeleted():
                    self._outputMetadata(e_record, metadataPrefix, metadata)
                # XXX about
        self._outputResuming(
            e_listRecords,
            self._server.listRecords,
            outputFunc,
            kw)
        return envelope

    def listSets(self, **kw):
        envelope, e_listSets = self._outputEnvelope(
            verb='ListSets', **kw)
        def outputFunc(element, sets, token_kw):
            for setSpec, setName, setDescription in sets:
                e_set = SubElement(e_listSets, nsoai('set'))
                e_setSpec = SubElement(e_set, nsoai('setSpec'))
                e_setSpec.text = setSpec
                e_setName = SubElement(e_set, nsoai('setName'))
                e_setName.text = setName
                # XXX ignore setDescription
        self._outputResuming(
            e_listSets,
            self._server.listSets,
            outputFunc,
            kw)
        return envelope

    def handleException(self, exception):
        if isinstance(exception, error.ErrorBase):
            envelope = self._outputErrors(
                [(exception.oainame(), str(exception))])
            return envelope
        # unhandled exception, so raise again
        raise
    
    def _outputBasicEnvelope(self, **kw):
        e_oaipmh = Element(nsoai('OAI-PMH'), nsmap=nsmap)
        e_oaipmh.set('{%s}schemaLocation' % NS_XSI,
                     ('http://www.openarchives.org/OAI/2.0/ '
                      'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd'))
        e_tree = ElementTree(element=e_oaipmh)
        e_responseDate = SubElement(e_oaipmh, nsoai('responseDate'))
        # date should be first possible moment
        e_responseDate.text = datetime_to_datestamp(
            datetime.utcnow().replace(microsecond=0))
        e_request = SubElement(e_oaipmh, nsoai('request'))
        for key, value in kw.items():
            if key == 'from_':
                key = 'from'
            if key == 'from' or key == 'until':
                value = datetime_to_datestamp(value)
            e_request.set(key, value)
        # XXX this is potentially slow..
        e_request.text = self._server.identify().baseURL()
        return e_tree, e_oaipmh
    
    def _outputEnvelope(self, **kw):
        e_tree, e_oaipmh = self._outputBasicEnvelope(**kw)
        e_element = SubElement(e_oaipmh, nsoai(kw['verb']))
        return e_tree, e_element

    def _outputErrors(self, errors, **kw):
        # only pass functional arguments
        e_tree, e_oaipmh = self._outputBasicEnvelope(**kw)
        for error_code, error_msg in errors:
            e_error = SubElement(e_oaipmh, nsoai('error'))
            e_error.set('code', error_code)
            e_error.text = error_msg
        return e_tree
    
    def _outputResuming(self, element, input_func, output_func, kw):
        if 'resumptionToken' in kw:
            resumptionToken = kw['resumptionToken']
            result, token = input_func(resumptionToken=resumptionToken)
            # unpack keywords from resumption token
            token_kw, dummy = decodeResumptionToken(resumptionToken)
        else:
            result, token = input_func(**kw)
            # if we don't get results for the first request,
            # then no records match
            # XXX this will also be triggered if there are no sets,
            # but input_func (listSets) should have already raised
            # NoSetHierarchyError in that case
            if not result:
                raise error.NoRecordsMatchError,\
                      "No records match for request."
            # without resumption token keys are fine
            token_kw = kw
        output_func(element, result, token_kw)
        if token is not None:
            e_resumptionToken = SubElement(element, nsoai('resumptionToken'))
            e_resumptionToken.text = token
            
    def _outputHeader(self, element, header):
        e_header = SubElement(element, nsoai('header'))
        if header.isDeleted():
            e_header.set('status', 'deleted')
        e_identifier = SubElement(e_header, nsoai('identifier'))
        e_identifier.text = header.identifier()
        e_datestamp = SubElement(e_header, nsoai('datestamp'))
        e_datestamp.text = datetime_to_datestamp(header.datestamp())
        for set in header.setSpec():
            e = SubElement(e_header, nsoai('setSpec'))
            e.text = set
    
    def _outputMetadata(self, element, metadata_prefix, metadata):
        e_metadata = SubElement(element, nsoai('metadata'))
        if not self._metadata_registry.hasWriter(metadata_prefix):
            raise error.CannotDisseminateFormatError,\
                  "Unknown metadata format: %s" % metadata_prefix
        self._metadata_registry.writeMetadata(
            metadata_prefix, e_metadata, metadata)

class Server(common.ResumptionOAIPMH):
    """A server that responds to messages by returning OAI-PMH compliant XML.

    Takes a server object complying with the OAIPMH interface.
    """
    def __init__(self, server, metadata_registry=None,
                 resumption_batch_size=10):
        self._tree_server = XMLTreeServer(server, metadata_registry,
                                          resumption_batch_size)

    def handleRequest(self, request_kw):
        """Handles incoming OAI-PMH request.

        request_kw is a dictionary containing request parameters, including
        verb.
        """
        # try to get verb, if not, we have an argument handling error
        try:
            new_kw = {}
            try:
                for key, value in request_kw.items():
                    new_kw[str(key)] = value
            except UnicodeError:
                raise error.BadVerbError,\
                      "Non-ascii keys in request."
            request_kw = new_kw
            try:
                verb = request_kw.pop('verb')
            except KeyError:
                verb = 'unknown'
                raise error.BadVerbError,\
                      "Required verb argument not found."
            if verb not in ['GetRecord', 'Identify', 'ListIdentifiers',
                            'ListMetadataFormats', 'ListRecords', 'ListSets']:
                raise error.BadVerbError, "Illegal verb: %s" % verb
            # replace from and until arguments if necessary
            from_ = request_kw.get('from')
            if from_ is not None:
                # rename to from_ for internal use
                request_kw['from_'] = datestamp_to_datetime(from_)
                del request_kw['from']
            until = request_kw.get('until')
            if until is not None:
                request_kw['until'] = datestamp_to_datetime(until)
            # now validate parameters
            try:
                validation.validateResumptionArguments(verb, request_kw)
            except validation.BadArgumentError, e:
                # have to raise this as a error.BadArgumentError
                raise error.BadArgumentError, str(e)
            # now handle verb
            return self.handleVerb(verb, request_kw)            
        except:
            # in case of exception, call exception handler
            return self.handleException(request_kw, sys.exc_info())
        
    def handleVerb(self, verb, kw):
        method = common.getMethodForVerb(self._tree_server, verb)
        return etree.tostring(method(**kw).getroot())    

    def handleException(self, kw, exc_info):
        type, value, traceback = exc_info
        return etree.tostring(
            self._tree_server.handleException(value).getroot())
    
class Resumption(common.ResumptionOAIPMH):
    """There are two interfaces:

    OAIPMH

    ResumptionOAIPMH

    The Resumption class can turn a plain OAIPMH interface into
    a ResumptionOAIPMH interface

    This implementation is not particularly efficient for large
    result sets, as the complete result set needs to be reconstructed each
    time.
    """
    def __init__(self, server, batch_size=10):
        self._server = server
        self._batch_size = batch_size
    
    def handleVerb(self, verb, kw):
        # do original query
        method = common.getMethodForVerb(self._server, verb)
        # if we're handling a resumption token
        if 'resumptionToken' in kw:
            kw, cursor = decodeResumptionToken(
                kw['resumptionToken'])
            end_batch = cursor + self._batch_size
            # do query again with original parameters
            result = method(**kw)
            # XXX defeat laziness of any generators..
            result = list(result)
            if end_batch < len(result):
                resumptionToken = encodeResumptionToken(
                    kw, end_batch)
            else:
                resumptionToken = None
            return result[cursor:end_batch], resumptionToken
        # we're not handling resumption token, so do request
        result = method(**kw)
        # now handle resumption system
        if verb in ['ListSets', 'ListIdentifiers', 'ListRecords']:
            # XXX defeat the laziness effect of any generators..
            result = list(result)
            end_batch = self._batch_size
            if end_batch < len(result):
                resumptionToken = encodeResumptionToken(
                    kw, end_batch)
            else:
                resumptionToken = None
            return result[0:end_batch], resumptionToken
        return result

def encodeResumptionToken(kw, cursor):
    kw = kw.copy()
    kw['cursor'] = str(cursor)
    from_ = kw.get('from_')
    if from_ is not None:
        kw['from_'] = datetime_to_datestamp(from_)
    until = kw.get('until')
    if until is not None:
        kw['until'] = datetime_to_datestamp(until)
    return urlencode(kw)

def decodeResumptionToken(token):
    token = str(token)
    try:
        kw = cgi.parse_qs(token, True, True)
    except ValueError:
        raise error.BadResumptionTokenError,\
              "Unable to decode resumption token: %s" % token
    result = {}
    for key, value in kw.items():
        value = value[0]
        if key == 'from_' or key == 'until':
            value = datestamp_to_datetime(value)
        result[key] = value
    try:
        cursor = int(result.pop('cursor'))
    except (KeyError, ValueError):
        raise error.BadResumptionTokenError,\
              "Unable to decode resumption token (bad cursor): %s" % token
    # XXX should also validate result contents. Need verb information
    # for this, and somewhat more flexible verb validation support
    return result, cursor
    
def oai_dc_writer(element, metadata):
    e_dc = SubElement(element, nsoaidc('dc'))
    e_dc.set('{%s}schemaLocation' % NS_XSI,
             '%s http://www.openarchives.org/OAI/2.0/oai_dc.xsd' % NS_DC)
    map = metadata.getMap()
    for name in [
        'title', 'creator', 'subject', 'description', 'publisher',
        'contributor', 'date', 'type', 'format', 'identifier',
        'source', 'language', 'relation', 'coverage', 'rights']:
        for value in map.get(name, []):
            e = SubElement(e_dc, nsdc(name))
            e.text = value
               
def nsoai(name):
    return '{%s}%s' % (NS_OAIPMH, name)

def nsoaidc(name):
    return '{%s}%s' % (NS_OAIDC, name)

def nsdc(name):
    return '{%s}%s' % (NS_DC, name)
