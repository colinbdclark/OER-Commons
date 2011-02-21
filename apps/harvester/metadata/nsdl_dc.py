from harvester.oaipmh.metadata import MetadataReader, global_metadata_registry
from harvester.metadata import MetadataFormat


nsdl_dc_reader = MetadataReader(
    fields={
    'dc_title':       ('textList', 'nsdl_dc:nsdl_dc/dc:title/text()'),
    'dct_alternative':       ('textList', 'nsdl_dc:nsdl_dc/dct:alternative/text()'),
    'dc_identifier':       ('textList', 'nsdl_dc:nsdl_dc/dc:identifier/text()'),
    'dc_subject':       ('textList', 'nsdl_dc:nsdl_dc/dc:subject/text()'),
    'dct_educationLevel':       ('textList', 'nsdl_dc:nsdl_dc/dct:educationLevel/text()'),
    'dct_audience':       ('textList', 'nsdl_dc:nsdl_dc/dct:audience/text()'),
    'dct_mediator':       ('textList', 'nsdl_dc:nsdl_dc/dct:mediator/text()'),
    'dc_description':       ('textList', 'nsdl_dc:nsdl_dc/dc:description/text()'),
    'dc_type':       ('textList', 'nsdl_dc:nsdl_dc/dc:type/text()'),
    'dc_rights':       ('textList', 'nsdl_dc:nsdl_dc/dc:rights/text()'),
    'dct_accessRights':       ('textList', 'nsdl_dc:nsdl_dc/dct:accessRights/text()'),
    'dct_license':       ('textList', 'nsdl_dc:nsdl_dc/dct:license/text()'),
    'dc_contributor':       ('textList', 'nsdl_dc:nsdl_dc/dc:contributor/text()'),
    'dc_creator':       ('textList', 'nsdl_dc:nsdl_dc/dc:creator/text()'),
    'dc_publisher':       ('textList', 'nsdl_dc:nsdl_dc/dc:publisher/text()'),
    'dc_language':       ('textList', 'nsdl_dc:nsdl_dc/dc:language/text()'),
    'dc_coverage':       ('textList', 'nsdl_dc:nsdl_dc/dc:coverage/text()'),
    'dct_spatial':       ('textList', 'nsdl_dc:nsdl_dc/dct:spatial/text()'),
    'dct_temporal':       ('textList', 'nsdl_dc:nsdl_dc/dct:temporal/text()'),
    'dc_date':       ('textList', 'nsdl_dc:nsdl_dc/dc:date/text()'),
    'dct_created':       ('textList', 'nsdl_dc:nsdl_dc/dct:created/text()'),
    'dct_available':       ('textList', 'nsdl_dc:nsdl_dc/dct:available/text()'),
    'dct_dateAccepted':       ('textList', 'nsdl_dc:nsdl_dc/dct:dateAccepted/text()'),
    'dct_dateCopyrighted':       ('textList', 'nsdl_dc:nsdl_dc/dct:dateCopyrighted/text()'),
    'dct_dateSubmitted':       ('textList', 'nsdl_dc:nsdl_dc/dct:dateSubmitted/text()'),
    'dct_issued':       ('textList', 'nsdl_dc:nsdl_dc/dct:issued/text()'),
    'dct_modified':       ('textList', 'nsdl_dc:nsdl_dc/dct:modified/text()'),
    'dct_valid':       ('textList', 'nsdl_dc:nsdl_dc/dct:valid/text()'),
    'ieee_interactivityType':       ('textList', 'nsdl_dc:nsdl_dc/ieee:interactivityType/text()'),
    'ieee_interactivityLevel':       ('textList', 'nsdl_dc:nsdl_dc/ieee:interactivityLevel/text()'),
    'ieee_typicalLearningTime':       ('textList', 'nsdl_dc:nsdl_dc/ieee:typicalLearningTime/text()'),
    'dc_format':       ('textList', 'nsdl_dc:nsdl_dc/dc:format/text()'),
    'dct_extent':       ('textList', 'nsdl_dc:nsdl_dc/dct:extent/text()'),
    'dct_medium':       ('textList', 'nsdl_dc:nsdl_dc/dct:medium/text()'),
    'dc_relation':       ('textList', 'nsdl_dc:nsdl_dc/dc:relation/text()'),
    'dct_conformsTo':       ('textList', 'nsdl_dc:nsdl_dc/dct:conformsTo/text()'),
    'dct_conformsTo':       ('textList', 'nsdl_dc:nsdl_dc/dct:conformsTo/text()'),
    'dct_isFormatOf':       ('textList', 'nsdl_dc:nsdl_dc/dct:isFormatOf/text()'),
    'dct_hasFormat':       ('textList', 'nsdl_dc:nsdl_dc/dct:hasFormat/text()'),
    'dct_isPartOf':       ('textList', 'nsdl_dc:nsdl_dc/dct:isPartOf/text()'),
    'dct_hasPart':       ('textList', 'nsdl_dc:nsdl_dc/dct:hasPart/text()'),
    'dct_isReferencedBy':       ('textList', 'nsdl_dc:nsdl_dc/dct:isReferencedBy/text()'),
    'dct_References':       ('textList', 'nsdl_dc:nsdl_dc/dct:References/text()'),
    'dct_isReplacedBy':       ('textList', 'nsdl_dc:nsdl_dc/dct:isReplacedBy/text()'),
    'dct_replaces':       ('textList', 'nsdl_dc:nsdl_dc/dct:replaces/text()'),
    'dct_isRequiredBy':       ('textList', 'nsdl_dc:nsdl_dc/dct:isRequiredBy/text()'),
    'dct_requires':       ('textList', 'nsdl_dc:nsdl_dc/dct:requires/text()'),
    'dct_isVersionOf':       ('textList', 'nsdl_dc:nsdl_dc/dct:isVersionOf/text()'),
    'dct_hasVersion':       ('textList', 'nsdl_dc:nsdl_dc/dct:hasVersion/text()'),
    'dct_abstract':       ('textList', 'nsdl_dc:nsdl_dc/dct:abstract/text()'),
    'dct_tableOfContents':       ('textList', 'nsdl_dc:nsdl_dc/dct:tableOfContents/text()'),
    'dct_bibliographicCitation':       ('textList', 'nsdl_dc:nsdl_dc/dct:bibliographicCitation/text()'),
    'dct_instructionalMethod':       ('textList', 'nsdl_dc:nsdl_dc/dct:instructionalMethod/text()'),
    'dct_provenance':       ('textList', 'nsdl_dc:nsdl_dc/dct:provenance/text()'),
    'dct_accrualMethod':       ('textList', 'nsdl_dc:nsdl_dc/dct:accrualMethod/text()'),
    'dct_accrualPeriodicity':       ('textList', 'nsdl_dc:nsdl_dc/dct:accrualPeriodicity/text()'),
    'dct_accrualPolicy':       ('textList', 'nsdl_dc:nsdl_dc/dct:accrualPolicy/text()'),
    },
    namespaces={
    'nsdl_dc': 'http://ns.nsdl.org/nsdl_dc_v1.02/',
    'dc' : 'http://purl.org/dc/elements/1.1/',
    'dct' : 'http://purl.org/dc/terms/',
    'ieee' : 'http://www.ieee.org/xsd/LOMv1p0'}
    )


global_metadata_registry.registerReader('nsdl_dc', nsdl_dc_reader)    
global_metadata_registry.registerReader('nsdl_dc_1_02', nsdl_dc_reader)    
    
    
class NSDLDublinCore(MetadataFormat):
    
    header = (
            'OAI_IDENTIFIER',
            'DC_TITLE',
            'DCT_ALTERNATIVE',
            'DC_IDENTIFIER',
            'DC_SUBJECT',
            'DCT_EDUCATIONLEVEL',
            'DCT_AUDIENCE',
            'DCT_MEDIATOR',
            'DC_DESCRIPTION',
            'DC_TYPE',
            'DC_RIGHTS',
            'DCT_ACCESSRIGHTS',
            'DCT_LICENSE',
            'DC_CONTRIBUTOR',
            'DC_CREATOR',
            'DC_PUBLISHER',
            'DC_LANGUAGE',
            'DC_COVERAGE',
            'DCT_SPATIAL',
            'DCT_TEMPORAL',
            'DC_DATE',
            'DCT_CREATED',
            'DCT_AVAILABLE',
            'DCT_DATEACCEPTED',
            'DCT_DATECOPYRIGHTED',
            'DCT_DATESUBMITTED',
            'DCT_ISSUED',
            'DCT_MODIFIED',
            'DCT_VALID',
            'IEEE_INTERACTIVITYTYPE',
            'IEEE_INTERACTIVITYLEVEL',
            'IEEE_TYPICALLEARNINGTIME',
            'DC_FORMAT',
            'DCT_EXTENT',
            'DCT_MEDIUM',
            'DC_RELATION',
            'DCT_CONFORMSTO',
            'DCT_CONFORMSTO',
            'DCT_ISFORMATOF',
            'DCT_HASFORMAT',
            'DCT_ISPARTOF',
            'DCT_HASPART',
            'DCT_ISREFERENCEDBY',
            'DCT_REFERENCES',
            'DCT_ISREPLACEDBY',
            'DCT_REPLACES',
            'DCT_ISREQUIREDBY',
            'DCT_REQUIRES',
            'DCT_ISVERSIONOF',
            'DCT_HASVERSION',
            'DCT_ABSTRACT',
            'DCT_TABLEOFCONTENTS',
            'DCT_BIBLIOGRAPHICCITATION',
            'DCT_INSTRUCTIONALMETHOD',
            'DCT_PROVENANCE',
            'DCT_ACCRUALMETHOD',
            'DCT_ACCRUALPERIODICITY',
            'DCT_ACCRUALPOLICY',
        )
    
    def process_record(self, identifier, metadata):

        metadata_map = metadata.getMap()

        data = {}        
        data["oai_identifier"] = identifier
        data["dc_title"] = metadata_map.get('dc_title',[])
        data["dct_alternative"] = metadata_map.get('dct_alternative',[])
        data["dc_identifier"] = metadata_map.get('dc_identifier',[])
        data["dc_subject"] = metadata_map.get('dc_subject',[])
        data["dct_educationLevel"] = metadata_map.get('dct_educationLevel',[])
        data["dct_audience"] = metadata_map.get('dct_audience',[])
        data["dct_mediator"] = metadata_map.get('dct_mediator',[])
        data["dc_description"] = metadata_map.get('dc_description',[])
        data["dc_type"] = metadata_map.get('dc_type',[])
        data["dc_rights"] = metadata_map.get('dc_rights',[])
        data["dct_accessRights"] = metadata_map.get('dct_accessRights',[])
        data["dct_license"] = metadata_map.get('dct_license',[])
        data["dc_contributor"] = metadata_map.get('dc_contributor',[])
        data["dc_creator"] = metadata_map.get('dc_creator',[])
        data["dc_publisher"] = metadata_map.get('dc_publisher',[])
        data["dc_language"] = metadata_map.get('dc_language',[])
        data["dc_coverage"] = metadata_map.get('dc_coverage',[])
        data["dct_spatial"] = metadata_map.get('dct_spatial',[])
        data["dct_temporal"] = metadata_map.get('dct_temporal',[])
        data["dc_date"] = metadata_map.get('dc_date',[])
        data["dct_created"] = metadata_map.get('dct_created',[])
        data["dct_available"] = metadata_map.get('dct_available',[])
        data["dct_dateAccepted"] = metadata_map.get('dct_dateAccepted',[])
        data["dct_dateCopyrighted"] = metadata_map.get('dct_dateCopyrighted',[])
        data["dct_dateSubmitted"] = metadata_map.get('dct_dateSubmitted',[])
        data["dct_issued"] = metadata_map.get('dct_issued',[])
        data["dct_modified"] = metadata_map.get('dct_modified',[])
        data["dct_valid"] = metadata_map.get('dct_valid',[])
        data["ieee_interactivityType"] = metadata_map.get('ieee_interactivityType',[])
        data["ieee_interactivityLevel"] = metadata_map.get('ieee_interactivityLevel',[])
        data["ieee_typicalLearningTime"] = metadata_map.get('ieee_typicalLearningTime',[])
        data["dc_format"] = metadata_map.get('dc_format',[])
        data["dct_extent"] = metadata_map.get('dct_extent',[])
        data["dct_medium"] = metadata_map.get('dct_medium',[])
        data["dc_relation"] = metadata_map.get('dc_relation',[])
        data["dct_conformsTo"] = metadata_map.get('dct_conformsTo',[])
        data["dct_conformsTo"] = metadata_map.get('dct_conformsTo',[])
        data["dct_isFormatOf"] = metadata_map.get('dct_isFormatOf',[])
        data["dct_hasFormat"] = metadata_map.get('dct_hasFormat',[])
        data["dct_isPartOf"] = metadata_map.get('dct_isPartOf',[])
        data["dct_hasPart"] = metadata_map.get('dct_hasPart',[])
        data["dct_isReferencedBy"] = metadata_map.get('dct_isReferencedBy',[])
        data["dct_References"] = metadata_map.get('dct_References',[])
        data["dct_isReplacedBy"] = metadata_map.get('dct_isReplacedBy',[])
        data["dct_replaces"] = metadata_map.get('dct_replaces',[])
        data["dct_isRequiredBy"] = metadata_map.get('dct_isRequiredBy',[])
        data["dct_requires"] = metadata_map.get('dct_requires',[])
        data["dct_isVersionOf"] = metadata_map.get('dct_isVersionOf',[])
        data["dct_hasVersion"] = metadata_map.get('dct_hasVersion',[])
        data["dct_abstract"] = metadata_map.get('dct_abstract',[])
        data["dct_tableOfContents"] = metadata_map.get('dct_tableOfContents',[])
        data["dct_bibliographicCitation"] = metadata_map.get('dct_bibliographicCitation',[])
        data["dct_instructionalMethod"] = metadata_map.get('dct_instructionalMethod',[])
        data["dct_provenance"] = metadata_map.get('dct_provenance',[])
        data["dct_accrualMethod"] = metadata_map.get('dct_accrualMethod',[])
        data["dct_accrualPeriodicity"] = metadata_map.get('dct_accrualPeriodicity',[])
        data["dct_accrualPolicy"] = metadata_map.get('dct_accrualPolicy',[])
    
        return (data["oai_identifier"],
                "|".join(data["dc_title"]).encode('utf-8'),
                "|".join(data["dct_alternative"]).encode('utf-8'),
                "|".join(data["dc_identifier"]).encode('utf-8'),
                "|".join(data["dc_subject"]).encode('utf-8'),
                "|".join(data["dct_educationLevel"]).encode('utf-8'),
                "|".join(data["dct_audience"]).encode('utf-8'),
                "|".join(data["dct_mediator"]).encode('utf-8'),
                "|".join(data["dc_description"]).encode('utf-8'),
                "|".join(data["dc_type"]).encode('utf-8'),
                "|".join(data["dc_rights"]).encode('utf-8'),
                "|".join(data["dct_accessRights"]).encode('utf-8'),
                "|".join(data["dct_license"]).encode('utf-8'),
                "|".join(data["dc_contributor"]).encode('utf-8'),
                "|".join(data["dc_creator"]).encode('utf-8'),
                "|".join(data["dc_publisher"]).encode('utf-8'),
                "|".join(data["dc_language"]).encode('utf-8'),
                "|".join(data["dc_coverage"]).encode('utf-8'),
                "|".join(data["dct_spatial"]).encode('utf-8'),
                "|".join(data["dct_temporal"]).encode('utf-8'),
                "|".join(data["dc_date"]).encode('utf-8'),
                "|".join(data["dct_created"]).encode('utf-8'),
                "|".join(data["dct_available"]).encode('utf-8'),
                "|".join(data["dct_dateAccepted"]).encode('utf-8'),
                "|".join(data["dct_dateCopyrighted"]).encode('utf-8'),
                "|".join(data["dct_dateSubmitted"]).encode('utf-8'),
                "|".join(data["dct_issued"]).encode('utf-8'),
                "|".join(data["dct_modified"]).encode('utf-8'),
                "|".join(data["dct_valid"]).encode('utf-8'),
                "|".join(data["ieee_interactivityType"]).encode('utf-8'),
                "|".join(data["ieee_interactivityLevel"]).encode('utf-8'),
                "|".join(data["ieee_typicalLearningTime"]).encode('utf-8'),
                "|".join(data["dc_format"]).encode('utf-8'),
                "|".join(data["dct_extent"]).encode('utf-8'),
                "|".join(data["dct_medium"]).encode('utf-8'),
                "|".join(data["dc_relation"]).encode('utf-8'),
                "|".join(data["dct_conformsTo"]).encode('utf-8'),
                "|".join(data["dct_conformsTo"]).encode('utf-8'),
                "|".join(data["dct_isFormatOf"]).encode('utf-8'),
                "|".join(data["dct_hasFormat"]).encode('utf-8'),
                "|".join(data["dct_isPartOf"]).encode('utf-8'),
                "|".join(data["dct_hasPart"]).encode('utf-8'),
                "|".join(data["dct_isReferencedBy"]).encode('utf-8'),
                "|".join(data["dct_References"]).encode('utf-8'),
                "|".join(data["dct_isReplacedBy"]).encode('utf-8'),
                "|".join(data["dct_replaces"]).encode('utf-8'),
                "|".join(data["dct_isRequiredBy"]).encode('utf-8'),
                "|".join(data["dct_requires"]).encode('utf-8'),
                "|".join(data["dct_isVersionOf"]).encode('utf-8'),
                "|".join(data["dct_hasVersion"]).encode('utf-8'),
                "|".join(data["dct_abstract"]).encode('utf-8'),
                "|".join(data["dct_tableOfContents"]).encode('utf-8'),
                "|".join(data["dct_bibliographicCitation"]).encode('utf-8'),
                "|".join(data["dct_instructionalMethod"]).encode('utf-8'),
                "|".join(data["dct_provenance"]).encode('utf-8'),
                "|".join(data["dct_accrualMethod"]).encode('utf-8'),
                "|".join(data["dct_accrualPeriodicity"]).encode('utf-8'),
                "|".join(data["dct_accrualPolicy"]).encode('utf-8'),
            )