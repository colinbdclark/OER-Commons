from common.models import MediaFormat
from django.template.loader import render_to_string
from haystack.models import SearchResult
from materials.models.common import GeneralSubject, Language, \
    GeographicRelevance
from materials.models.course import Course
from materials.models.library import Library
from materials.utils import get_name_from_id, get_slug_from_id
from oai.oer import OERMetadataFormat


MEDIA_FORMAT_TO_DC_TYPE_MAPPING = {
  'audio':'Sound',
  'graphics-photos':'Image',
  'text-html':'Text',
  'video':'MovingImage',
}


class OAIDublinCore(OERMetadataFormat):

    def build_metadata(self, item, site):
        if isinstance(item, SearchResult):
            search_result = item
            item = search_result.object
        else:
            search_result = None

        title = item.title
        description = item.abstract
        if item.published_on:
            date = item.published_on

        content_type = []
        if search_result:
            creator = search_result.authors
            if search_result.general_subjects:
                subject = [get_name_from_id(GeneralSubject, int(id)) for id in search_result.general_subjects]

            if search_result.media_formats:
                for id in search_result.media_formats:
                    id = int(id)
                    slug = get_slug_from_id(MediaFormat, id)
                    if slug in MEDIA_FORMAT_TO_DC_TYPE_MAPPING:
                        content_type.append(MEDIA_FORMAT_TO_DC_TYPE_MAPPING[slug])
            if search_result.languages:
                language = [get_slug_from_id(Language, int(id)) for id in search_result.languages]
            if search_result.geographic_relevance:
                coverage = [get_name_from_id(GeographicRelevance, int(id)) for id in search_result.geographic_relevance]

        else:
            creator = item.authors.all().values_list("name", flat=True)
            subject = item.general_subjects.all().values_list("name", flat=True)
            if isinstance(item, (Course, Library)):
                for slug in item.media_formats.all().values_list("slug", flat=True):
                    if slug in MEDIA_FORMAT_TO_DC_TYPE_MAPPING:
                        content_type.append(MEDIA_FORMAT_TO_DC_TYPE_MAPPING[slug])
            language = item.languages.all().values_list("slug", flat=True)
            coverage = item.geographic_relevance.all().values_list("name", flat=True)

        if isinstance(item, Library):
            content_type.append("Collection")

        rights = item.license.name
        identifier = "http://%s%s" % (site.domain, item.get_absolute_url())

        return render_to_string("oai/oer/oai_dc.xml", locals())
