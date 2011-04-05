from harvester.oaipmh import error

class Header:
    def __init__(self, identifier, datestamp, setspec, deleted):
        self._identifier = identifier
        self._datestamp = datestamp
        self._setspec = setspec
        self._deleted = deleted
        
    def identifier(self):
        return self._identifier
    
    def datestamp(self):
        return self._datestamp

    def setSpec(self):
        return self._setspec

    def isDeleted(self):
        return self._deleted

class Metadata:
    def __init__(self, map):
        self._map = map

    def getMap(self):
        return self._map
    
    def getField(self, name):
        return self._map[name]

    __getitem__ = getField
    
class Identify:
    def __init__(self, repositoryName, baseURL, protocolVersion, adminEmails,
                 earliestDatestamp, deletedRecord, granularity, compression):
        self._repositoryName = repositoryName
        self._baseURL = baseURL
        self._protocolVersion = protocolVersion
        self._adminEmails = adminEmails
        self._earliestDatestamp = earliestDatestamp
        self._deletedRecord = deletedRecord
        self._granularity = granularity
        self._compression = compression
        # XXX description
        
    def repositoryName(self):
        return self._repositoryName

    def baseURL(self):
        return self._baseURL

    def protocolVersion(self):
        return self._protocolVersion

    def adminEmails(self):
        return self._adminEmails

    def earliestDatestamp(self):
        return self._earliestDatestamp

    def deletedRecord(self):
        return self._deletedRecord

    def granularity(self):
        return self._granularity

    def compression(self):
        return self._compression
    
def ResumptionTokenSpec(dict):
    dict = dict.copy()
    dict['resumptionToken'] = 'exclusive'
    return dict

class OAIMethodImpl(object):
    def __init__(self, verb):
        self._verb = verb
        
    def __call__(self, bound_self, **kw):
        return bound_self.handleVerb(self._verb, kw)
        
def OAIMethod(verb):
    obj = OAIMethodImpl(verb)
    def method(self, **kw):
        return obj(self, **kw)
    return method

class OAIPMH:
    """Mixin that implements the Python-level OAI-PMH interface.

    It does not include resumptionToken handling.
    
    It passes the calls on to the 'handleVerb' method, which should be
    overridden in a subclass.
    """
    def handleVerb(self, verb, kw):
        raise NotImplementedError
    
    getRecord = OAIMethod(
        'GetRecord',
        )
    
    identify = OAIMethod(
        'Identify',
        )

    listIdentifiers = OAIMethod(
        'ListIdentifiers',
        )

    listMetadataFormats = OAIMethod(
        'ListMetadataFormats',
        )

    listRecords = OAIMethod(
        'ListRecords',
        )

    listSets = OAIMethod(
        'ListSets',
        )
    
class ResumptionOAIPMH:
    """Mixin that implements the Resumption-capable OAI-PMH interface.

    It passes the arguments on to the 'handleVerb' method, which
    should be overridden in a subclass.

    The listIdentifiers, listSets and listRecords methods return
    tuples of a list and resumptionToken. If the resumptionToken
    returned is None, this indicates the end of the list is reached.
    """

    def handleVerb(self, verb, kw):
        raise NotImplementedError
    
    getRecord = OAIMethod(
        'GetRecord',
        )
    
    identify = OAIMethod(
        'Identify',
        )

    listIdentifiers = OAIMethod(
        'ListIdentifiers',
        )

    listMetadataFormats = OAIMethod(
        'ListMetadataFormats',
        )

    listRecords = OAIMethod(
        'ListRecords',
        )

    listSets = OAIMethod(
        'ListSets',
        )

def getMethodForVerb(server, verb):
    return getattr(server, verb[0].lower() + verb[1:])

