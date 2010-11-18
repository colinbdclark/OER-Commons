from haystack import site
from haystack.fields import CharField, MultiValueField, IntegerField
from haystack.indexes import SearchIndex
from materials.models.course import Course



class CourseIndex(SearchIndex):

    text = CharField(document=True, use_template=True)
    title = CharField(model_attr="title")
    keywords = MultiValueField(model_attr="indexed_keywords")
    collection = IntegerField(model_attr="collection__id")
    institution = IntegerField(model_attr="institution__id")
    general_subjects = MultiValueField(model_attr="indexed_general_subjects")
    grade_levels = MultiValueField(model_attr="indexed_grade_levels")


    def get_queryset(self):
        return Course.objects.all()


site.register(Course, CourseIndex)
