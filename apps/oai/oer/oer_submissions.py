from django.template.loader import render_to_string
from haystack.models import SearchResult
from materials.models.course import Course
from materials.models.library import Library
from materials.models.material import RATED, REVIEWED, TAGGED
from oai.oer import OERMetadataFormat


class OERSubmissions(OERMetadataFormat):

    def get_items(self, *args, **kwargs):
        query = super(OERSubmissions, self).get_items(*args, **kwargs)
        return query.filter(member_activities__in=[RATED, REVIEWED, TAGGED])

    def build_metadata(self, item, site):
        if isinstance(item, SearchResult):
            search_result = item
            item = search_result.object
        else:
            search_result = None

        url = "http://%s%s" % (site.domain, item.get_absolute_url())
        if isinstance(item, (Course, Library)):
            native_id = item.provider_id

        tags = item.tags.all().distinct().values_list("name", flat=True)
        rating = item.rating
        total_rates = item.ratings.all().count()
        reviews = item.reviews.all().values_list("text", flat=True)

        return render_to_string("oai/oer/oer_submissions.xml", locals())
