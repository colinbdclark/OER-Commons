from django.template.loader import render_to_string
from haystack.models import SearchResult
from materials.models.common import GeneralSubject
from materials.utils import get_name_from_id
from oai.oer import OERMetadataFormat


class OERRecommender(OERMetadataFormat):

    def build_metadata(self, item, site):
        if isinstance(item, SearchResult):
            search_result = item
            item = search_result.object
        else:
            search_result = None

        title = item.title
        abstract = item.abstract
        if item.published_on:
            date = item.published_on
        url = item.url
        oer_url = "http://%s%s" % (site.domain, item.get_absolute_url())
        identifier = self.repository.build_header(item).identifier


        if search_result:
            authors = search_result.authors
            if search_result.general_subjects:
                keywords = [get_name_from_id(GeneralSubject, slug) for slug in search_result.general_subjects]

        else:
            authors = item.authors.all().values_list("name", flat=True)
            keywords = item.general_subjects.all().values_list("name", flat=True)

        return render_to_string("oai/oer/oer_recommender.xml", locals())
