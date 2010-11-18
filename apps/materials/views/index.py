from django.views.generic.simple import direct_to_template
from materials.models.common import GeneralSubject, GradeLevel
from haystack.query import SearchQuerySet


class VocabularyFilter(object):

    def __init__(self, index_name, request_name, model):
        self.index_name = index_name
        self.request_name = request_name
        self.model = model

    @property
    def available_values(self):
        return self.model.objects.all().values_list("slug", flat=True)

    def extract_value(self, request):
        value = request.REQUEST.getlist(self.request_name)
        if not value:
            return None
        available_values = self.available_values
        value = [v for v in value if v in available_values]
        if not value:
            return None
        if set(value) == set(available_values):
            return None
        if len(value) == 1:
            return self.model.objects.get(slug=value[0]).id
        return list(self.model.objects.filter(slug__in=value).values_list("id", flat=True))

    def update_query(self, query, request):
        value = self.extract_value(request)
        if not value:
            return query
        if isinstance(value, list):
            kwargs = {"%s__in" % self.index_name: value}
            return query.filter(**kwargs)
        kwargs = {"%s" % self.index_name: value}
        return query.filter(**kwargs)


FILTERS = {
    "general_subjects": VocabularyFilter("general_subjects", "f.general_subject", GeneralSubject),
    "grade_levels": VocabularyFilter("grade_levels", "f.edu_level", GradeLevel),
}


def index(request, facet_fields=["general_subjects", "grade_levels"]):

    batch_start = 0
    batch_size = 20
    order_by = "title_s"

    query = SearchQuerySet()
    for filter in FILTERS.values():
        query = filter.update_query(query, request)

    for facet_field in facet_fields:
        query = query.facet(facet_field)

    batch_end = batch_start + batch_size
    results = query.order_by(order_by).load_all()[batch_start:batch_end]
    facets = query.facet_counts()

    import pprint
    pprint.pprint(facets)

    return direct_to_template(request, "materials/index.html", locals())
