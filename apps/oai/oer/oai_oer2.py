from common.models import GeneralSubject
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from haystack.models import SearchResult
from materials.models.common import  Language, \
    GeographicRelevance, MediaFormat, GradeLevel, Collection
from materials.models.community import CommunityType, CommunityItem
from materials.models.course import Course, CourseMaterialType
from materials.models.library import Library, LibraryMaterialType
from materials.utils import get_name_from_id, get_slug_from_id
from oai.oer import OERMetadataFormat


DATETIME_FORMAT_LRE3 = '%Y-%m-%dT%H:%M:%S.00Z'


def build_vcard(data):
    text = """<![CDATA[BEGIN:VCARD\n"""
    text += """VERSION:3.0\n"""
    for k, v in data:
        text += """%s:%s\n""" % (k, v)
    text += """END:VCARD
]]>"""
    return text


def grade_level_to_age_range(grade_levels):
    start = u''
    end = u''
    if 'Primary' in grade_levels:
        start = u'6'
    elif 'Secondary' in grade_levels:
        start = u'13'
    elif 'Post-secondary' in grade_levels:
        start = u'18'

    if 'Post-secondary' in grade_levels:
        end = u'U'
    elif 'Secondary' in grade_levels:
        end = u'18'
    elif 'Primary' in grade_levels:
        end = u'12'

    return u'%s-%s' % (start, end)


class OAIOER2(OERMetadataFormat):

    def build_metadata(self, item, site):
        if isinstance(item, SearchResult):
            search_result = item
            item = search_result.object
        else:
            search_result = None

        languages = []
        geographic_relevance = []
        authors = []
        identifier = self.repository.build_header(item).identifier
        media_formats = []
        course_material_types = []
        library_material_types = []
        community_types = []
        grade_levels = []
        license = item.license
        collection = None

        if search_result:
            if search_result.languages:
                languages = [get_slug_from_id(Language, int(id)) for id in search_result.languages]
            if search_result.geographic_relevance:
                geographic_relevance = [get_name_from_id(GeographicRelevance, int(id)) for id in search_result.geographic_relevance]
            authors = search_result.authors
            if search_result.media_formats:
                media_formats = [get_slug_from_id(MediaFormat, int(id)) for id in search_result.media_formats]
            if search_result.course_material_types:
                course_material_types = [get_name_from_id(CourseMaterialType, int(id)) for id in search_result.course_material_types]
            if search_result.library_material_types:
                library_material_types = [get_name_from_id(LibraryMaterialType, int(id)) for id in search_result.library_material_types]
            if search_result.community_types:
                community_types = [get_name_from_id(CommunityType, int(id)) for id in search_result.community_types]
            if search_result.grade_levels:
                grade_levels = [get_name_from_id(GradeLevel, int(id)) for id in search_result.grade_levels]
            if search_result.collection:
                collection = Collection.objects.get(pk=int(search_result.collection))
            if search_result.general_subjects:
                general_subjects = [get_name_from_id(GeneralSubject, int(id)) for id in search_result.general_subjects]

        else:
            languages = item.languages.values_list("slug", flat=True)
            geographic_relevance = item.geographic_relevance.all().values_list("name", flat=True)
            authors = item.authors.all().values_list("name", flat=True)
            if isinstance(item, (Course, Library)):
                media_formats = item.media_formats.values_list("slug", flat=True)
                collection = item.collection
            if isinstance(item, Course):
                course_material_types = item.material_types.all().values_list("name", flat=True)
            if isinstance(item, Library):
                library_material_types = item.material_types.all().values_list("name", flat=True)
            if isinstance(item, CommunityItem):
                community_types = item.community_types.all().values_list("name", flat=True)
            grade_levels = item.grade_levels.all().values_list("name", flat=True)
            general_subjects = item.general_subjects.all().values_list("name", flat=True)

        general = {}
        general["identifier"] = [{'catalog':self.repository.identifier, 'entry': identifier}]
        if isinstance(item, (Course, Library)):
            if item.collection and item.provider_id:
                general['identifier'].append({'catalog':item.collection.name, 'entry':item.provider_id})

        general["title"] = item.title
        general["description"] = item.abstract
        general["keyword"] = item.keywords.all().values_list("name", flat=True)

        if languages:
            general["language"] = languages
        else:
            general["language"] = ["en"]

        general["coverage"] = geographic_relevance

        life_cycle = {}
        life_cycle["contribute"] = []
        if authors:
            for name in authors:
                author = dict(role="author", entity=build_vcard([('N', name), ('FN', name)]))
                if item.content_creation_date:
                    author['date'] = item.content_creation_date.strftime(DATETIME_FORMAT_LRE3)
                life_cycle['contribute'].append(author)

        if isinstance(item, (Course, Library)):
            if item.institution:
                institution = {'role':'publisher'}
                institution['entity'] = build_vcard([('N', item.institution.name),
                                                    ('FN', item.institution.name),
                                                    ('ORG', item.institution.name)])
                if item.content_creation_date:
                    institution['date'] = item.content_creation_date.strftime(DATETIME_FORMAT_LRE3)
                life_cycle['contribute'].append(institution)

        meta_metadata = {}
        meta_metadata["identifier"] = dict(catalog=self.repository.identifier,
                                           entry=identifier[len(self.repository.identifier_prefix):])
        meta_metadata["language"] = general["language"][0]

        technical = {}
        technical["format"] = media_formats
        technical["location"] = "http://%s%s" % (site.domain, item.get_absolute_url())
        technical["installationRemarks"] = item.tech_requirements

        educational = {}
        educational["learningResourceType"] = course_material_types or library_material_types or  community_types or []
        educational["context"] = grade_levels
        educational["typicalagerange"] = grade_level_to_age_range(grade_levels)
        if isinstance(item, (Course, Library)):
            educational["description"] = item.curriculum_standards

        rights = {}
        if not license.name or 'public domain' in license.name.lower() or license.name.lower() == 'no license':
            rights['copyrightAndOtherRestrictions'] = 'no'
        else:
            rights['copyrightAndOtherRestrictions'] = 'yes'

        _description = u""
        if license.copyright_holder:
            _description += u'Copyright Holder: %s' % license.copyright_holder
        if license.description or license.name:
            _description += '\n\n%s' % (license.description or license.name)
        if license.url:
            _description += '\n\n%s' % license.url
        rights['description'] = {"en": _description.strip()}

        if license.type.startswith("cc-"):
            rights['description']['x-t-cc-url'] = license.url

        relation = {}
        if collection:
            relation["description"] = collection.name
            relation["identifier"] = "http://%s%s" % (site.domain,
                      reverse("materials:%s:collection_index" % item.namespace,
                              kwargs=dict(collection=collection.slug)))

        annotation = []
        for review in item.reviews.all().select_related():
            _name = u"%s %s" % (review.user.first_name, review.user.last_name)
            _name = _name.strip()
            annotation.append({
                 'entity': build_vcard([('N', _name), ('FN', _name)]),
                 'description': review['text'],
                 'date': review.timestamp.strftime(DATETIME_FORMAT_LRE3)
            })

        classification = general_subjects
        if item.published_on:
            published_on = item.published_on.strftime(DATETIME_FORMAT_LRE3)

        return render_to_string("oai/oer/oai_oer2.xml", locals())
