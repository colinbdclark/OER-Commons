from authoring.models import AuthoredMaterial
from haystack.fields import IntegerField, CharField, MultiValueField
from haystack.sites import site
from materials.search_indexes import MaterialSearchIndex, AuthorsField, \
    VocabularyMultiValueField


class AuthoredMaterialSearchIndex(MaterialSearchIndex):

    creator = IntegerField(model_attr="author__id")

    abstract = CharField(model_attr="abstract", weight=2.0)
    url = CharField(model_attr="url", stored=True, indexed=False)

    authors = AuthorsField(model_attr="authors", weight=1.0)
    keywords = MultiValueField(model_attr="keyword_slugs")
    keywords_names = MultiValueField(model_attr="keyword_names", weight=3.0)
    general_subjects = VocabularyMultiValueField(model_attr="general_subjects")
    grade_levels = VocabularyMultiValueField(model_attr="all_grade_levels")
    grade_sublevels = VocabularyMultiValueField(model_attr="all_grade_sublevels")
    grades = VocabularyMultiValueField(model_attr="all_grades")
    media_formats = VocabularyMultiValueField(model_attr="media_formats")
    languages = VocabularyMultiValueField(model_attr="languages")
    course_material_types = VocabularyMultiValueField(model_attr="material_types")
    collection = IntegerField(model_attr="collection__id", null=True)
    collection_name = CharField(model_attr="collection__name", weight=2.0, null=True)


site.register(AuthoredMaterial, AuthoredMaterialSearchIndex)
