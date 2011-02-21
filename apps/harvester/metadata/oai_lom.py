from harvester.metadata import MetadataFormat
from harvester.oaipmh import common
from harvester.oaipmh.metadata import Error, global_metadata_registry
from lxml import etree
import re


def unique(s):
    return list(set(s))


def getLOMText(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return ''
    if el is None:
        return ''
    return el.text    

def getLOMVocabularyValue(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return ''
    if el is None:
        return ''
    value_el = el.find('./{http://ltsc.ieee.org/xsd/LOM}value')
    return value_el is not None and value_el.text or ''    

def getLOMDateTime(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return ''
    if el is None:
        return ''
    dateTime_el = el.find('./{http://ltsc.ieee.org/xsd/LOM}dateTime')
    return dateTime_el is not None and dateTime_el.text or ''    

def getLOMLangString(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {}
    strings = el.findall('{http://ltsc.ieee.org/xsd/LOM}string')
    for s in strings:
        value[s.get('language')] = s.text
    return value

def getLOMIdentifier(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'catalog':'', 'entry':''}
    value['catalog'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}catalog'))
    value['entry'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}entry'))
    return value

def getLOMContribute(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'role':'', 'entity':[], 'date':''}
    value['role'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}role'))
    value['entity'] = [e.text for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}entity')]
    value['date'] = getLOMDateTime(el.find('./{http://ltsc.ieee.org/xsd/LOM}date'))
    return value

def getLOMDuration(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'duration':'', 'description':{}}
    value['duration'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}duration'))
    value['description'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}description'))
    return value

def getLOMRelation(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'kind':'', 'resource':{}}
    value['kind'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}kind'))
    value['resource'] = getLOMResource(el.find('./{http://ltsc.ieee.org/xsd/LOM}resource'))
    return value

def getLOMResource(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'identifier':[], 'description':[]}
    value['identifier'] = [getLOMIdentifier(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}identifier')]
    value['description'] = [getLOMLangString(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}description')]
    return value

def getLOMAnnotation(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'entity':'', 'date':'', 'description':{}}
    value['entity'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}entity'))
    value['date'] = getLOMDateTime(el.find('./{http://ltsc.ieee.org/xsd/LOM}date'))
    value['description'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}description'))
    return value

def getLOMGeneral(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'identifier':[], 'title': {}, 'language':[],
             'description':[], 'keyword': [], 'coverage': [],
             'structure':'', 'aggregationLevel':''}
    value['identifier'] = [getLOMIdentifier(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}identifier')]
    value['title'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}title'))
    value['language'] = [e.text for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}language')]
    value['description'] = [getLOMLangString(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}description')]
    value['keyword'] = [getLOMLangString(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}keyword')]
    value['coverage'] = [getLOMLangString(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}coverage')]
    value['structure'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}structure')) 
    value['aggregationLevel'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}aggregationLevel')) 
    return value

def getLOMLifeCycle(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'version':{}, 'status': '', 'contribute':[]}
    value['version'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}version'))
    value['status'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}status'))
    value['contribute'] = [getLOMContribute(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}contribute')]
    return value

def getLOMMetaMetadata(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'identifier':[], 'contribute': [], 'metadataSchema':[],
             'language':''}
    value['identifier'] = [getLOMIdentifier(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}identifier')]
    value['contribute'] = [getLOMContribute(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}contribute')]
    value['metadataSchema'] = [e.text for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}metadataSchema')]
    value['language'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}language'))
    return value

def getLOMOrComposite(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'type':'', 'name':'', 'minimumVersion':'', 'maximumVersion':''}
    value['type'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}type'))
    value['name'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}name'))
    value['minimumVersion'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}minimumVersion'))
    value['maximumVersion'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}maximumVersion'))
    return value


def getLOMRequirement(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'orComposite':[]}
    value['orComposite'] = [getLOMOrComposite(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}orComposite')]
    return value


def getLOMTechical(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'format':[], 'size': '', 'location':[], 'requirement': [],
             'installationRemarks': {}, 'otherPlatformRequirements': {},
             'duration': {}}
    value['format'] = [e.text for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}format')]
    value['size'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}size'))
    value['location'] = [e.text for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}location')]
    value['requirement'] = [getLOMRequirement(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}requirement')]
    value['installationRemarks'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}installationRemarks'))
    value['otherPlatformRequirements'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}otherPlatformRequirements'))
    value['duration'] = getLOMDuration(el.find('./{http://ltsc.ieee.org/xsd/LOM}duration'))
    return value

def getLOMEducational(el):
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
    value['interactivityType'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}interactivityType'))
    value['learningResourceType'] = [getLOMVocabularyValue(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}learningResourceType')]
    value['interactivityLevel'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}interactivityLevel'))
    value['semanticDensity'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}semanticDensity'))
    value['intendedEndUserRole'] = [getLOMVocabularyValue(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}intendedEndUserRole')]
    value['context'] = [getLOMVocabularyValue(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}context')]
    value['typicalAgeRange'] = [getLOMLangString(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}typicalAgeRange')]
    value['difficulty'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}difficulty'))
    value['typicalLearningTime'] = getLOMDuration(el.find('./{http://ltsc.ieee.org/xsd/LOM}typicalLearningTime'))
    value['description'] = [getLOMLangString(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}description')]
    value['language'] = [e.text for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}language')]
    return value

def getLOMRights(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'cost':'', 'copyrightAndOtherRestrictions': '',
             'description':{}}
    value['cost'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}cost'))
    value['copyrightAndOtherRestrictions'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}copyrightAndOtherRestrictions'))
    value['description'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}description'))
    return value

def getLOMTaxon(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'id':'', 'entry': {}}
    value['id'] = getLOMText(el.find('./{http://ltsc.ieee.org/xsd/LOM}id'))
    value['entry'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}entry'))
    return value

def getLOMTaxonPath(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'source':{}, 'taxon': []}
    value['source'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}source'))
    value['taxon'] = [getLOMTaxon(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}taxon')]
    return value

def getLOMClassification(el):
    if isinstance(el, list) and el:
        el = el[0]
    elif isinstance(el, list) and not el:
        return {}
    if el is None:
        return {}
    value = {'purpose':'', 'taxonPath': [], 'description':{},
             'keyword':[]}
    value['purpose'] = getLOMVocabularyValue(el.find('./{http://ltsc.ieee.org/xsd/LOM}purpose'))
    value['taxonPath'] = [getLOMTaxonPath(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}taxonPath')]
    value['description'] = getLOMLangString(el.find('./{http://ltsc.ieee.org/xsd/LOM}description'))
    value['keyword'] = [getLOMLangString(e) for e in el.findall('./{http://ltsc.ieee.org/xsd/LOM}keyword')]
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
            elif field_type == 'LOM:General':
                el = e(expr)
                value = getLOMGeneral(el)
            elif field_type == 'LOM:LifeCycle':
                el = e(expr)
                value = getLOMLifeCycle(el)
            elif field_type == 'LOM:MetaMetadata':
                el = e(expr)
                value = getLOMMetaMetadata(el)
            elif field_type == 'LOM:Technical':
                el = e(expr)
                value = getLOMTechical(el)
            elif field_type == 'LOM:EducationalList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getLOMEducational(el))
            elif field_type == 'LOM:Rights':
                el = e(expr)
                value = getLOMRights(el)
            elif field_type == 'LOM:RelationList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getLOMRelation(el))
            elif field_type == 'LOM:AnnotationList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getLOMAnnotation(el))
            elif field_type == 'LOM:ClassificationList':
                value = []
                els = e(expr)
                for el in els:                
                    value.append(getLOMClassification(el))
            else:
                raise Error, "Unknown field type: %s" % field_type
            map[field_name] = value
        return common.Metadata(map)

oai_lom_reader = MetadataReader(
    fields={
        'general': ('LOM:General', 'lom:lom/lom:general'),
        'lifeCycle': ('LOM:LifeCycle', 'lom:lom/lom:lifeCycle'),
        'metaMetadata': ('LOM:MetaMetadata', 'lom:lom/lom:metaMetadata'),
        'technical': ('LOM:Technical', 'lom:lom/lom:technical'),
        'educational': ('LOM:EducationalList', 'lom:lom/lom:educational'),
        'rights': ('LOM:Rights', 'lom:lom/lom:rights'),
        'relation': ('LOM:RelationList', 'lom:lom/lom:relation'),
        'annotation': ('LOM:AnnotationList', 'lom:lom/lom:annotation'),
        'classification': ('LOM:ClassificationList', 'lom:lom/lom:classification'),

    },
    namespaces={
        'lom': 'http://ltsc.ieee.org/xsd/LOM',
    }
)

global_metadata_registry.registerReader('oai_lom', oai_lom_reader)
global_metadata_registry.registerReader('LREv3.0', oai_lom_reader)
global_metadata_registry.registerReader('oai_lre3', oai_lom_reader)
global_metadata_registry.registerReader('oai_oer2', oai_lom_reader)


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
    if not 'contribute' in lifeCycle:
        return ''
    vcards = ["\n".join(c['entity']) for c in lifeCycle['contribute'] if c.get('entity') and c.get('role') == 'author']
    names = []
    for vcard in vcards:
        for line in vcard.split('\n'):
            if line.startswith('FN:'):
                name = line[3:].strip()
                name = " ".join([w.capitalize() for w in name.split()]) # Convert to title case
                names.append(name)
                break
    return names

def extractAuthorEmails(lifeCycle):
    if not 'contribute' in lifeCycle:
        return ''
    vcards = ["\n".join(c['entity']) for c in lifeCycle['contribute'] if c.get('entity') and c.get('role') == 'author']
    emails = []
    for vcard in vcards:
        for line in vcard.split('\n'):
            if line.startswith('EMAIL'):
                email = line.split(':',1)[1]
                emails.append(email)
                break
    return emails

def extractInstitution(lifeCycle):
    if not 'contribute' in lifeCycle:
        return ''
    vcards = ["\n".join(c['entity']) for c in lifeCycle['contribute'] if c.get('entity') and c.get('role') == 'publisher']
    if vcards:
        vcard = vcards[0]
        for line in vcard.split('\n'):
            if line.startswith('FN:'):
                return line[3:].strip()
    return ''

def extractSubjects(classification):
    subjects = []
    for cl in classification:
        if not cl.get('taxonPath'):
            continue
        for taxonPath in cl['taxonPath']:
            if not taxonPath.get('taxon'):
                continue
            for taxon in taxonPath['taxon']:
                if not taxon.get('entry'):
                    continue
                subjects.append(extractLangString(taxon['entry']))
    return subjects

def extractLearningResourceType(educational):
    lrt = []
    for ed in educational:
        if not ed.get('learningResourceType'):
            continue
        lrt += ed['learningResourceType']
    return lrt

def extractTechnicalFormat(technical):
    tf = []
    if technical.get('format'):
        tf += technical['format']
    FORMAT_MAPPING = {
      'audio/': 'Audio',
      'application/ogg': 'Audio',                  
      'image/': 'Graphics/Photos',                  
      'text/': 'Text/HTML',                  
      'application/msword': 'Downloadable docs',
      'application/pdf': 'Downloadable docs',                  
      'video/': 'Video',                  
    }
    for i, f in enumerate(tf):
        if not re.match('(application/)|(audio/)|(image/)|(text/)|(video/)', f):
            continue
        unknown_content_type = True
        for content_type_re, media_format in FORMAT_MAPPING.items():
            if re.match(content_type_re, f):
                unknown_content_type = False
                tf[i] = media_format
        if unknown_content_type:
            tf[i] = 'Other'
    tf = unique(tf)
    tf.sort()
    return tf

def extractEduLevel(educational):
    levels = []
    for ed in educational:
        for typicalAgeRange in ed.get('typicalAgeRange', []):
            levels.append(extractLangString(typicalAgeRange))
        for context in ed.get('context', []):
            levels.append(context)
    levels = unique(levels)
    return levels

def extractLicenseURL(rights):
    description = extractLangString(rights.get('description'))
    if not description:
        return ''
    URL_RE = 'http://\S+'
    urls = re.findall(URL_RE, description, re.I)
    if urls:
        return urls[0]
    return ''

def extractLicenseTitle(rights):
    url = extractLicenseURL(rights)
    if url and re.match('creativecommons.org', url, re.I):
        version = url.split('/')[-1] or url.split('/')[-2]
        if not version.match('[0-9]\.[0-9]'):
            version = ''
        else:
            version = ' ' + version
        if re.match('/by/', 'url', re.I):
            return 'Creative Commons Attribution' + version
        elif re.match('/by-sa/', 'url', re.I):
            return 'Creative Commons Attribution-ShareAlike' + version
        elif re.match('/by-nd/', 'url', re.I):
            return 'Creative Commons Attribution-NoDerivs' + version
        elif re.match('/by-nc/', 'url', re.I):
            return 'Creative Commons Attribution-NonCommercial' + version
        elif re.match('/by-nc-sa/', 'url', re.I):
            return 'Creative Commons Attribution-NonCommercial-ShareAlike' + version
        elif re.match('/by-nc-nd/', 'url', re.I):
            return 'Creative Commons Attribution-NoDerivs-NonCommercial' + version
    return extractLangString(rights.get('description'))

def extractURL(technical):
    location = technical.get('location')
    if location and location[0]:
        return location[0]
    return u''
  
    
class OAILOM(MetadataFormat):
    
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
        
        metadata_map = metadata.getMap()
        data = {}
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
        row.append(data["general"]['identifier'][0]['entry'].encode('utf-8')) # CR_NATIVE_ID
        row.append('') # CR_ENTRY_DATE
        row.append('') # CR_COURSE_ID
        row.append(extractLangString(data["general"]['title']).encode('utf-8')) # CR_TITLE
        row.append('') # CR_FCOLM
        row.append(extractCreateDate(data["lifeCycle"]).encode('utf-8')) # CR_CREATE_DATE
        row.append("|".join(extractAuthorNames(data["lifeCycle"])).encode('utf-8')) # CR_AUTHOR_NAME
        row.append("|".join(extractAuthorEmails(data["lifeCycle"])).encode('utf-8')) # CR_AUTHOR_EMAIL
        row.append('') # CR_AUTHOR_COUNTRY
        row.append(extractInstitution(data["lifeCycle"]).encode('utf-8')) # CR_INSTITUTION
        row.append(extractURL(data["technical"]).encode('utf-8')) # CR_URL
        row.append('No') # CR_IS_PART_OF_OCW
        row.append('') # CR_COLLECTION
        row.append("|".join(extractSubjects(data["classification"])).encode('utf-8')) # CR_SUBJECT
        row.append("|".join(extractLearningResourceType(data["educational"])).encode('utf-8')) # CR_MATERIAL_TYPE
        row.append("|".join(extractTechnicalFormat(data["technical"])).encode('utf-8')) # CR_MEDIA_FORMATS
        row.append(extractLangString(data["technical"].get('otherPlatformRequirements')).encode('utf-8')) # CR_NOTABLE_REQS
        row.append("|".join(extractEduLevel(data["educational"])).encode('utf-8')) # CR_LEVEL
        row.append("\n".join([extractLangString(d) for d in data["general"]['description']]).encode('utf-8')) # CR_ABSTRACT
        row.append("|".join([extractLangString(k) for k in data["general"]['keyword']]).encode('utf-8')) # CR_KEYWORDS
        row.append("|".join([l for l in data["general"]['language']]).encode('utf-8')) # CR_LANGUAGE
        row.append("|".join([extractLangString(c) for c in data["general"]['coverage']]).encode('utf-8')) # CR_IRR
        row.append('') # CR_PREREQ_TITLE1
        row.append('') # CR_PREREQ_URL1
        row.append('') # CR_PREREQ_TITLE2
        row.append('') # CR_PREREQ_URL2
        row.append('') # CR_POSTREQ_TITLE1
        row.append('') # CR_POSTREQ_URL1
        row.append('') # CR_POSTREQ_TITLE2
        row.append('') # CR_POSTREQ_URL2
        row.append(extractLicenseURL(data["rights"]).encode('utf-8')) # CR_COU_URL
        row.append(extractLicenseTitle(data["rights"]).encode('utf-8')) # CR_COU_TITLE
        row.append(extractLangString(data["rights"].get('description')).encode('utf-8')) # CR_COU_DESCRIPTION
        row.append('') # CR_COU_COPYRIGHT_HOLDER
        row.append('') # CR_PARENT_MODIFIED
        row.append('') # CR_PARENT_TITLE
        row.append('') # CR_PARENT_URL
        row.append('') # CR_PARENT_CHANGES
        row.append('') # CR_CKSUM
        row.append('') # CR_CURRIC_STANDARDS
        return row
        