from haystack.models import SearchResult
from materials.models.common import Collection
from materials.models.course import Course
from materials.models.library import Library
from oai.metadata import Header
from oai.repository import Repository
from oai.set import Set


class OERRepository(Repository):

    def get_sets(self, item):
        if isinstance(item, (Course, Library)):
            collection = item.collection
            if collection:
                return ["collection:%s" % collection.slug]
        else:
            return []

    def build_header(self, item):
        if isinstance(item, SearchResult):
            item = item.object
        identifier = "%s%s.%s.%i" % (self.identifier_prefix,
                                     item._meta.app_label,
                                     item._meta.module_name,
                                     item.id)
        datestamp = item.published_on
        sets = self.get_sets(item)
        return Header(identifier, datestamp, sets)

    def list_sets(self):
        sets = []
        for slug, name in Collection.objects.values_list("slug", "name"):
            sets.append(Set("collection:%s" % slug, name))
        return sets
