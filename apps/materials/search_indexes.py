from haystack import site
from haystack.fields import CharField, MultiValueField, IntegerField, \
    BooleanField, DateTimeField, FloatField
from materials.models.community import CommunityItem
from materials.models.course import Course
from materials.models.library import Library
from rubrics.indexes import EvaluatedItemIndex
from core.search import SearchIndex
import re


class SortableTitleField(CharField):

    REMOVED_PREFIX_RE = re.compile(r"^[^\w]*(the|a|an)[\s]+", re.I | re.U)
    PUNCTUATION_RE = re.compile(r"[^\w]+", re.U)

    def convert(self, value):
        value = self.REMOVED_PREFIX_RE.sub(u"", value)
        value = self.PUNCTUATION_RE.sub(u"", value)
        return value


class VocabularyMultiValueField(MultiValueField):

    def convert(self, value):
        if isinstance(value, list):
            return [isinstance(v, int) and v or v.id for v in value]
        return value.values_list("id", flat=True)


class AuthorsField(MultiValueField):

    def convert(self, value):
        if isinstance(value, list):
            return value
        return value.values_list("name", flat=True)


class ByField(MultiValueField):

    def convert(self, value):
        if isinstance(value, list):
            return value
        return value.values_list("user__id", flat=True)


class AlignmentTagsField(MultiValueField):

    def convert(self, value):
        if isinstance(value, list):
            return list(set(value))
        return value.values_list("tag__id", flat=True).order_by().distinct()


class MaterialSearchIndex(SearchIndex, EvaluatedItemIndex):

    text = CharField(document=True, use_template=True)
    slug = CharField(model_attr="slug", stored=True, indexed=False)
    title = CharField(model_attr="title", weight=10.0)
    sortable_title = SortableTitleField(model_attr="title")
    published_on = DateTimeField(model_attr="published_on", null=True)
    featured = BooleanField(model_attr="featured")
    featured_on = DateTimeField(model_attr="featured_on", null=True)

    member_activities = MultiValueField(model_attr="member_activities")
    rating = FloatField(model_attr="rating")

    saved_by = ByField(model_attr="saved_items")
    tagged_by = ByField(model_attr="tags")
    rated_by = ByField(model_attr="ratings")
    reviewed_by = ByField(model_attr="reviews")

    saved_in_folders = MultiValueField(model_attr="saved_in_folders")

    creator = IntegerField(model_attr="creator__id")

    license = CharField(model_attr="license__type", null=True)
    cou_bucket = CharField(model_attr="license__bucket", null=True)

    microsites = VocabularyMultiValueField(model_attr="microsites")
    topics = VocabularyMultiValueField(model_attr="topics")
    indexed_topics = VocabularyMultiValueField(model_attr="indexed_topics")

    workflow_state = CharField(model_attr="workflow_state")
    is_displayed = BooleanField(model_attr="is_displayed")

    visits = IntegerField(model_attr="visits")

    alignment_standards = MultiValueField(model_attr="alignment_standards")
    alignment_grades = MultiValueField(model_attr="alignment_grades")
    alignment_categories = MultiValueField(model_attr="alignment_categories")
    alignment_tags = AlignmentTagsField(model_attr="alignment_tags")


class CourseIndex(MaterialSearchIndex):

    abstract = CharField(model_attr="abstract", weight=2.0)
    url = CharField(model_attr="url", stored=True, indexed=False)
    keywords = MultiValueField(model_attr="keyword_slugs")
    keywords_names = MultiValueField(model_attr="keyword_names", weight=3.0)
    authors = AuthorsField(model_attr="authors", weight=1.0)
    collection = IntegerField(model_attr="collection__id", null=True)
    collection_name = CharField(model_attr="collection__name", weight=2.0, null=True)
    institution = IntegerField(model_attr="institution__id", null=True)
    institution_name = CharField(model_attr="institution__name", null=True, weight=1.0)
    general_subjects = VocabularyMultiValueField(model_attr="general_subjects")
    grade_levels = VocabularyMultiValueField(model_attr="grade_levels")
    course_material_types = VocabularyMultiValueField(model_attr="material_types")
    media_formats = VocabularyMultiValueField(model_attr="media_formats")
    languages = VocabularyMultiValueField(model_attr="languages")
    geographic_relevance = VocabularyMultiValueField(model_attr="geographic_relevance")

    course_or_module = CharField(model_attr="course_or_module")


class LibraryIndex(MaterialSearchIndex):

    abstract = CharField(model_attr="abstract", weight=2.0)
    url = CharField(model_attr="url", stored=True, indexed=False)
    keywords = MultiValueField(model_attr="keyword_slugs")
    keywords_names = MultiValueField(model_attr="keyword_names", weight=3.0)
    authors = AuthorsField(model_attr="authors", weight=1.0)
    collection = IntegerField(model_attr="collection__id", null=True)
    collection_name = CharField(model_attr="collection__name", weight=2.0, null=True)
    institution = IntegerField(model_attr="institution__id", null=True)
    institution_name = CharField(model_attr="institution__name", weight=1.0, null=True)
    general_subjects = VocabularyMultiValueField(model_attr="general_subjects")
    grade_levels = VocabularyMultiValueField(model_attr="grade_levels")
    library_material_types = VocabularyMultiValueField(model_attr="material_types")
    media_formats = VocabularyMultiValueField(model_attr="media_formats")
    languages = VocabularyMultiValueField(model_attr="languages")
    geographic_relevance = VocabularyMultiValueField(model_attr="geographic_relevance")


class CommunityItemIndex(MaterialSearchIndex):

    abstract = CharField(model_attr="abstract", weight=2.0)
    url = CharField(model_attr="url", stored=True, indexed=False)
    keywords = MultiValueField(model_attr="keyword_slugs")
    keywords_names = MultiValueField(model_attr="keyword_names", weight=3.0)
    authors = AuthorsField(model_attr="authors", weight=1.0)
    general_subjects = VocabularyMultiValueField(model_attr="general_subjects")
    grade_levels = VocabularyMultiValueField(model_attr="grade_levels")
    community_types = VocabularyMultiValueField(model_attr="community_types")
    community_topics = VocabularyMultiValueField(model_attr="community_topics")
    languages = VocabularyMultiValueField(model_attr="languages")
    geographic_relevance = VocabularyMultiValueField(model_attr="geographic_relevance")


site.register(Course, CourseIndex)
site.register(Library, LibraryIndex)
site.register(CommunityItem, CommunityItemIndex)
