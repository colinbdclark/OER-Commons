from authoring.models import AuthoredMaterial
from haystack.fields import IntegerField, CharField, MultiValueField
from haystack.sites import site
from materials.search_indexes import MaterialSearchIndex, AuthorsField, \
    VocabularyMultiValueField


class AuthoredMaterialSearchIndex(MaterialSearchIndex):

    creator = IntegerField(model_attr="author__id")

    abstract = CharField(model_attr="abstract", weight=2.0)

    authors = AuthorsField(model_attr="authors", weight=1.0)
    keywords = MultiValueField(model_attr="keyword_slugs")
    keywords_names = MultiValueField(model_attr="keyword_names", weight=3.0)
    general_subjects = VocabularyMultiValueField(model_attr="general_subjects")
    grade_levels = VocabularyMultiValueField(model_attr="grade_levels")
    media_formats = VocabularyMultiValueField(model_attr="media_formats")
    languages = VocabularyMultiValueField(model_attr="languages")


site.register(AuthoredMaterial, AuthoredMaterialSearchIndex)
