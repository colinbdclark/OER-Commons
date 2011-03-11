from django.db import models
from haystack.models import SearchResult
from haystack.query import SearchQuerySet
from materials.models.common import Collection
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from materials.models.material import PUBLISHED_STATE
from oai.exceptions import IdDoesNotExist
from oai.metadata import MetadataFormat, Header


class OERMetadataFormat(MetadataFormat):

    schema = "http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
    namespace = "http://www.openarchives.org/OAI/2.0/oai_dc/"

    def supported_by(self, item):
        if isinstance(item, (Course, Library, CommunityItem)):
            return True
        return False

    def get_items(self, from_date=None, until_date=None, set=None,
                  microsite=None):
        query = SearchQuerySet().narrow("workflow_state:%s" % PUBLISHED_STATE)
        if from_date:
            query = query.filter(published_on__gte=from_date)
        if until_date:
            query = query.filter(published_on__lte=until_date)

        if set is not None:
            set_name, slug = set.split(":")
            if set_name == "collection":
                query = query.narrow("collection:%i" % Collection.objects.get(slug=slug).id)

        if microsite:
            query = query.narrow("microsites:%i" % microsite.id)

        return query.order_by("published_on").load_all()

