

class OAIError(Exception):

    code = None


class BadResimptionToken(OAIError):

    code = "badResumptionToken"


class BadArgument(OAIError):

    code = "badArgument"


class InvalidMetadataPrefix(OAIError):

    code = "cannotDisseminateFormat"


class NoRecordsMatch(OAIError):

    code = "noRecordsMatch"


class NoSetHierarchy(OAIError):

    code = "noSetHierarchy"


class IdDoesNotExist(OAIError):

    code = "idDoesNotExist"


class NoMetadataFormats(OAIError):

    code = "noMetadataFormats"
