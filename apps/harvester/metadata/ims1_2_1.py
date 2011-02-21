from harvester.metadata import MetadataFormat
from harvester.oaipmh import common
from harvester.oaipmh.metadata import global_metadata_registry, Error
from lxml import etree
import re


def getIMSText(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return ''
    if el is None:
        return ''
    return el.text    

def getIMSVocabularyValue(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return ''
    if el is None:
        return ''
    value_el = el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}value')
    return value_el is not None and value_el.text or ''    

def getIMSDateTime(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return ''
    if el is None:
        return ''
    dateTime_el = el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}dateTime')
    return dateTime_el is not None and dateTime_el.text or ''    

def getIMSLangString(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {}
    strings = el.findall('{http://www.imsglobal.org/xsd/imsmd_v1p2}langstring')
    for s in strings:
        value[s.get('xml:lang')] = s.text
    return value

def getIMSIdentifier(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'catalog':'', 'entry':''}
    value['catalog'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}catalog'))
    value['entry'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}entry'))
    return value

def getIMSContribute(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'role':'', 'entity':[], 'date':''}
    value['role'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}role'))
    value['vcard'] = [e.text for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}centity/{http://www.imsglobal.org/xsd/imsmd_v1p2}vcard')]
    value['date'] = getIMSDateTime(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}date'))
    return value

def getIMSDuration(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'duration':'', 'description':{}}
    value['duration'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}duration'))
    value['description'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}description'))
    return value

def getIMSRelation(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'kind':'', 'resource':{}}
    value['kind'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}kind'))
    value['resource'] = getIMSResource(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}resource'))
    return value

def getIMSResource(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'identifier':[], 'description':[]}
    value['identifier'] = [getIMSIdentifier(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}identifier')]
    value['description'] = [getIMSLangString(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}description')]
    return value

def getIMSAnnotation(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'entity':'', 'date':'', 'description':{}}
    value['entity'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}entity'))
    value['date'] = getIMSDateTime(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}date'))
    value['description'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}description'))
    return value

def getIMSGeneral(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'identifier':[], 'title': {}, 'language':[],
             'description':[], 'keyword': [], 'coverage': [],
             'structure':'', 'aggregationLevel':''}
    value['identifier'] = [getIMSIdentifier(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}identifier')]
    value['title'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}title'))
    value['language'] = [e.text for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}language')]
    value['description'] = [getIMSLangString(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}description')]
    value['keyword'] = [getIMSLangString(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}keyword')]
    value['coverage'] = [getIMSLangString(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}coverage')]
    value['structure'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}structure')) 
    value['aggregationLevel'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}aggregationLevel')) 
    return value

def getIMSLifeCycle(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'version':{}, 'status': '', 'contribute':[]}
    value['version'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}version'))
    value['status'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}status'))
    value['contribute'] = [getIMSContribute(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}contribute')]
    return value

def getIMSMetaMetadata(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'identifier':[], 'contribute': [], 'metadataSchema':[],
             'language':''}
    value['identifier'] = [getIMSIdentifier(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}identifier')]
    value['contribute'] = [getIMSContribute(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}contribute')]
    value['metadataSchema'] = [e.text for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}metadataSchema')]
    value['language'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}language'))
    return value

def getIMSOrComposite(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'type':'', 'name':'', 'minimumVersion':'', 'maximumVersion':''}
    value['type'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}type'))
    value['name'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}name'))
    value['minimumVersion'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}minimumVersion'))
    value['maximumVersion'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}maximumVersion'))
    return value


def getIMSRequirement(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'orComposite':[]}
    value['orComposite'] = [getIMSOrComposite(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}orComposite')]
    return value


def getIMSTechical(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'format':[], 'size': '', 'location':[], 'requirement': [],
             'installationRemarks': {}, 'otherPlatformRequirements': {},
             'duration': {}}
    value['format'] = [e.text for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}format')]
    value['size'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}size'))
    value['location'] = [e.text for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}location')]
    value['requirement'] = [getIMSRequirement(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}requirement')]
    value['installationRemarks'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}installationRemarks'))
    value['otherPlatformRequirements'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}otherPlatformRequirements'))
    value['duration'] = getIMSDuration(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}duration'))
    return value

def getIMSEducational(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'interactivityType':'', 'learningResourceType': [],
             'interactivityLevel':'', 'semanticDensity': '',
             'intendedEndUserRole': [], 'context': [],
             'typicalAgeRange': [], 'difficulty':'',
             'typicalLearningTime':{}, 'description':[],
             'language':[]}
    value['interactivityType'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}interactivityType'))
    value['learningResourceType'] = [getIMSVocabularyValue(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}learningResourceType')]
    value['interactivityLevel'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}interactivityLevel'))
    value['semanticDensity'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}semanticDensity'))
    value['intendedEndUserRole'] = [getIMSVocabularyValue(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}intendedEndUserRole')]
    value['context'] = [getIMSVocabularyValue(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}context')]
    value['typicalAgeRange'] = [getIMSLangString(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}typicalAgeRange')]
    value['difficulty'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}difficulty'))
    value['typicalLearningTime'] = getIMSDuration(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}typicalLearningTime'))
    value['description'] = [getIMSLangString(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}description')]
    value['language'] = [e.text for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}language')]
    return value

def getIMSRights(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'cost':'', 'copyrightAndOtherRestrictions': '',
             'description':{}}
    value['cost'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}cost'))
    value['copyrightAndOtherRestrictions'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}copyrightAndOtherRestrictions'))
    value['description'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}description'))
    return value

def getIMSTaxon(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'id':'', 'entry': {}}
    value['id'] = getIMSText(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}id'))
    value['entry'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}entry'))
    return value

def getIMSTaxonPath(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'source':{}, 'taxon': []}
    value['source'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}source'))
    value['taxon'] = [getIMSTaxon(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}taxon')]
    return value

def getIMSClassification(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'purpose':'', 'taxonPath': [], 'description':{},
             'keyword':[]}
    value['purpose'] = getIMSVocabularyValue(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}purpose'))
    value['taxonPath'] = [getIMSTaxonPath(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}taxonPath')]
    value['description'] = getIMSLangString(el.find('./{http://www.imsglobal.org/xsd/imsmd_v1p2}description'))
    value['keyword'] = [getIMSLangString(e) for e in el.findall('./{http://www.imsglobal.org/xsd/imsmd_v1p2}keyword')]
    return value


class MetadataReader:
    def __init__(self, fields, namespaces=None):
        self._fields = fields
        self._namespaces = namespaces or {}

    def __call__(self, element):
        
        map = {}
        
        # create XPathEvaluator for this element
        xpath_evaluator = etree.XPathEvaluator(element, namespaces=self._namespaces)
        
        e = xpath_evaluator.evaluate
        # now extra field info according to xpath expr
        for field_name, (field_type, expr) in self._fields.items():
            if field_type == 'bytes':
                value = str(e(expr))
            elif field_type == 'bytesList':
                value = [str(item) for item in e(expr)]
            elif field_type == 'text':
                value = e(expr)
                if isinstance(value, list):
                    if value:
                        value = value[0]
                    else:
                        value = ''
            elif field_type == 'textList':
                value = e(expr)
            elif field_type == 'IMS:General':
                el = e(expr)
                value = getIMSGeneral(el)
            elif field_type == 'IMS:LifeCycle':
                el = e(expr)
                value = getIMSLifeCycle(el)
            elif field_type == 'IMS:MetaMetadata':
                el = e(expr)
                value = getIMSMetaMetadata(el)
            elif field_type == 'IMS:Technical':
                el = e(expr)
                value = getIMSTechical(el)
            elif field_type == 'IMS:EducationalList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getIMSEducational(el))
            elif field_type == 'IMS:Rights':
                el = e(expr)
                value = getIMSRights(el)
            elif field_type == 'IMS:RelationList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getIMSRelation(el))
            elif field_type == 'IMS:AnnotationList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getIMSAnnotation(el))
            elif field_type == 'IMS:ClassificationList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getIMSClassification(el))
            else:
                raise Error, "Unknown field type: %s" % field_type
            map[field_name] = value
        return common.Metadata(map)

ims1_2_1_reader = MetadataReader(
    fields={
        'general': ('IMS:General', 'ims1_2_1:lom/ims1_2_1:general'),
        'lifeCycle': ('IMS:LifeCycle', 'ims1_2_1:lom/ims1_2_1:lifecycle'),
        'metaMetadata': ('IMS:MetaMetadata', 'ims1_2_1:lom/ims1_2_1:metaMetadata'),
        'technical': ('IMS:Technical', 'ims1_2_1:lom/ims1_2_1:technical'),
        'educational': ('IMS:EducationalList', 'ims1_2_1:lom/ims1_2_1:educational'),
        'rights': ('IMS:Rights', 'ims1_2_1:lom/ims1_2_1:rights'),
        'relation': ('IMS:RelationList', 'ims1_2_1:lom/ims1_2_1:relation'),
        'annotation': ('IMS:AnnotationList', 'ims1_2_1:lom/ims1_2_1:annotation'),
        'classification': ('IMS:ClassificationList', 'ims1_2_1:lom/ims1_2_1:classification'),

    },
    namespaces={
        'ims1_2_1': 'http://www.imsglobal.org/xsd/imsmd_v1p2',
    }
)

global_metadata_registry.registerReader('ims1_2_1', ims1_2_1_reader)
  

def extractLangString(lang_string):
    if not lang_string:
        return ''
    if 'en' in lang_string:
        value = lang_string['en']
    else:
        value = lang_string.values()[0]
    if value is None:
        return ''
    return value

def extractCreateDate(lifeCycle):
    if not 'contribute' in lifeCycle:
        return ''
    dates = [c['date'] for c in lifeCycle['contribute'] if c.get('date')]
    if not dates:
        return ''
    return min(dates)

def extractAuthorNames(lifeCycle):
    names = []
    for contribute in lifeCycle['contribute']:
        for vcard in contribute['vcard']:
            for line in vcard.split('\n'):
                if line.startswith('FN:'):
                    name = line[3:].strip()
                    name = " ".join([w.capitalize() for w in name.split()]) # Convert to title case
                    names.append(name)
                    break
    return names

def extractAuthorEmails(lifeCycle):
    emails = []
    for contribute in lifeCycle['contribute']:
        for vcard in contribute['vcard']:
            for line in vcard.split('\n'):
                if line.startswith('EMAIL'):
                    email = line.split(':',1)[1]
                    emails.append(email)
                    break
    return emails

def extractSubjects(classification):
    subjects = []
    for cl in classification:
        if not cl.get('keyword'):
            continue
        for keyword in cl['keyword']:
            subjects.append(extractLangString(keyword))
    return subjects

def extractLicenseURL(rights):
    description = extractLangString(rights['description'])
    if not description:
        return ''
    URL_RE = 'http://\S+'
    urls = re.findall(URL_RE, description, re.I)
    if urls:
        return urls[0]
    return ''

    
class IMS1_2_1(MetadataFormat):

    header = (
            'CR_ID',
            'CR_NATIVE_ID',
            'CR_ENTRY_DATE',
            'CR_COURSE_ID',
            'CR_TITLE',
            'CR_FCOLM',
            'CR_CREATE_DATE',
            'CR_AUTHOR_NAME',
            'CR_AUTHOR_EMAIL',
            'CR_AUTHOR_COUNTRY',
            'CR_INSTITUTION',
            'CR_URL',
            'CR_IS_PART_OF_OCW',
            'CR_COLLECTION',
            'CR_SUBJECT',
            'CR_MATERIAL_TYPE',
            'CR_MEDIA_FORMATS',
            'CR_NOTABLE_REQS',
            'CR_LEVEL',
            'CR_ABSTRACT',
            'CR_KEYWORDS',
            'CR_LANGUAGE',
            'CR_IRR',
            'CR_PREREQ_TITLE1',
            'CR_PREREQ_URL1',
            'CR_PREREQ_TITLE2',
            'CR_PREREQ_URL2',
            'CR_POSTREQ_TITLE1',
            'CR_POSTREQ_URL1',
            'CR_POSTREQ_TITLE2',
            'CR_POSTREQ_URL2',
            'CR_COU_URL',
            'CR_COU_TITLE',
            'CR_COU_DESCRIPTION',
            'CR_COU_COPYRIGHT_HOLDER',
            'CR_PARENT_MODIFIED',
            'CR_PARENT_TITLE',
            'CR_PARENT_URL',
            'CR_PARENT_CHANGES',
            'CR_CKSUM',
            'CR_CURRIC_STANDARDS',
        )
    
    def process_record(self, identifier, metadata):
        
        data = {}
        metadata_map = metadata.getMap()
        data["oai_identifier"] = identifier
        data["general"] = metadata_map.get('general', {})
        data["lifeCycle"] = metadata_map.get('lifeCycle', {})
        data["metaMetadata"] = metadata_map.get('metaMetadata', {})
        data["technical"] = metadata_map.get('technical', {})
        data["educational"] = metadata_map.get('educational', [])
        data["rights"] = metadata_map.get('rights', {})
        data["relation"] = metadata_map.get('relation', [])
        data["annotation"] = metadata_map.get('annotation', [])
        data["classification"] = metadata_map.get('classification', [])
        
        
        row = []
        
        row.append('') # CR_ID
        row.append('') # CR_NATIVE_ID
        row.append('') # CR_ENTRY_DATE
        row.append('') # CR_COURSE_ID
        row.append(extractLangString(data["general"]['title']).encode('utf-8')) # CR_TITLE
        row.append('') # CR_FCOLM
        row.append(extractCreateDate(data["lifeCycle"]).encode('utf-8')) # CR_CREATE_DATE
        row.append("|".join(extractAuthorNames(data["lifeCycle"])).encode('utf-8')) # CR_AUTHOR_NAME
        row.append("|".join(extractAuthorEmails(data["lifeCycle"])).encode('utf-8')) # CR_AUTHOR_EMAIL
        row.append('') # CR_AUTHOR_COUNTRY
        row.append('') # CR_INSTITUTION
        row.append(data["technical"]['location'][0]) # CR_URL
        row.append('') # CR_IS_PART_OF_OCW
        row.append('') # CR_COLLECTION
        row.append("|".join(extractSubjects(data["classification"])).encode('utf-8')) # CR_SUBJECT
        row.append('') # CR_MATERIAL_TYPE
        row.append('') # CR_MEDIA_FORMATS
        row.append('') # CR_NOTABLE_REQS
        row.append('') # CR_LEVEL
        row.append("\n".join([extractLangString(d) for d in data["general"]['description']]).encode('utf-8')) # CR_ABSTRACT
        row.append("|".join([extractLangString(k) for k in data["general"]['keyword'] if extractLangString(k)]).encode('utf-8')) # CR_KEYWORDS
        row.append("|".join([l for l in data["general"]['language'] if l]).encode('utf-8')) # CR_LANGUAGE
        row.append('') # CR_IRR
        row.append('') # CR_PREREQ_TITLE1
        row.append('') # CR_PREREQ_URL1
        row.append('') # CR_PREREQ_TITLE2
        row.append('') # CR_PREREQ_URL2
        row.append('') # CR_POSTREQ_TITLE1
        row.append('') # CR_POSTREQ_URL1
        row.append('') # CR_POSTREQ_TITLE2
        row.append('') # CR_POSTREQ_URL2
        row.append(extractLicenseURL(data["rights"]).encode('utf-8')) # CR_COU_URL
        row.append('') # CR_COU_TITLE
        row.append('') # CR_COU_DESCRIPTION
        row.append('') # CR_COU_COPYRIGHT_HOLDER
        row.append('') # CR_PARENT_MODIFIED
        row.append('') # CR_PARENT_TITLE
        row.append('') # CR_PARENT_URL
        row.append('') # CR_PARENT_CHANGES
        row.append('') # CR_CKSUM
        row.append('') # CR_CURRIC_STANDARDS
        return row
        
