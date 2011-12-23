from common.models import Grade, GradeLevel
from curriculum.models import TaggedMaterial, AlignmentTag, Standard,\
    LearningObjectiveCategory
from django.http import Http404
from materials.models.common import Keyword, GeneralSubject,\
    MediaFormat, Language, GeographicRelevance, Collection, COU_BUCKETS, \
    LICENSE_TYPES
from materials.models.community import CommunityType, CommunityTopic
from materials.models.course import COURSE_OR_MODULE, CourseMaterialType
from materials.models.library import LibraryMaterialType
from materials.models.material import MEMBER_ACTIVITY_TYPES
from materials.models.microsite import Microsite, Topic
from materials.utils import get_name_from_slug
from ordereddict import OrderedDict
from rubrics.models import get_rubric_choices
from tags.models import Tag
from utils.templatetags.utils import truncatechars
import re


class Filter(object):

    def extract_value(self, request):
        raise NotImplemented()

    def update_query(self, query, value):
        raise NotImplemented()

    def update_query_string_params(self, query_string_params, value):
        raise NotImplemented()

    def page_subtitle(self, value):
        raise NotImplemented()


class VocabularyFilter(Filter):

    def __init__(self, index_name, request_name, model, title,
                 ignore_all_values=True):
        self.index_name = index_name
        self.request_name = request_name
        self.model = model
        self.title = title
        self.ignore_all_values = ignore_all_values

    @property
    def available_values(self):
        return set(self.model.objects.all().values_list("slug", flat=True))

    def extract_value(self, request):
        value = request.REQUEST.getlist(self.request_name)
        value = [v.strip() for v in value if v.strip()]
        if not value:
            return None
        return value

    def update_query(self, query, value):
        available_values = self.available_values


        if not isinstance(value, list):
            value = [value]

        if set(value) - available_values:
            raise Http404()

        if self.ignore_all_values and set(value) == available_values:
            return query

        value = list(self.model.objects.filter(slug__in=value).values_list("id", flat=True))

        return query.narrow(u"%s:(%s)" % (self.index_name, u" OR ".join([str(v) for v in value])))

    def update_query_string_params(self, query_string_params, value):
        query_string_params[self.request_name] = value
        return query_string_params

    def page_subtitle(self, value):
        if isinstance(value, list):
            return u"%s: %s" % (self.title, u", ".join([get_name_from_slug(self.model, v) for v in value]))
        return u"%s: %s" % (self.title, get_name_from_slug(self.model, value))


class ChoicesFilter(Filter):

    def __init__(self, index_name, request_name, choices, title):
        self.index_name = index_name
        self.request_name = request_name
        self.choices = choices
        self.title = title

    @property
    def available_values(self):
        return set([option[0] for option in self.choices])

    def extract_value(self, request):
        value = request.REQUEST.getlist(self.request_name)
        value = [v.strip() for v in value if v.strip()]
        if not value:
            return None
        return value

    def update_query(self, query, value):
        available_values = self.available_values

        if not isinstance(value, list):
            value = [value]

        if set(value) - available_values:
            raise Http404()

        if set(value) == available_values:
            return query

        return query.narrow(u"%s:(%s)" % (self.index_name, u" OR ".join([str(v) for v in value])))

    def update_query_string_params(self, query_string_params, value):
        query_string_params[self.request_name] = value
        return query_string_params

    def page_subtitle(self, value):
        choices_dict = dict(self.choices)
        if isinstance(value, list):
            return u"%s: %s" % (self.title, u", ".join([unicode(choices_dict[v]) for v in value]))
        return u"%s: %s" % (self.title, choices_dict[value])


class BooleanFilter(Filter):

    def __init__(self, index_name, request_name, title):
        self.index_name = index_name
        self.request_name = request_name
        self.title = title

    def extract_value(self, request):
        if request.REQUEST.get(self.request_name) == "yes":
            return True
        elif request.REQUEST.get(self.request_name) == "no":
            return False
        return None

    def update_query(self, query, value):
        return query.narrow(u"%s:%s" % (self.index_name, value and "true" or "false"))

    def update_query_string_params(self, query_string_params, value):
        query_string_params[self.request_name] = value and "yes" or "no"
        return query_string_params

    def page_subtitle(self, value):
        if value:
            return self.title
        else:
            return "Not %s" % self.title


class KeywordFilter(Filter):

    def __init__(self, index_name, request_name):
        self.index_name = index_name
        self.request_name = request_name

    @property
    def available_values(self):
        values = set(Keyword.objects.all().values_list("slug", flat=True))
        values.update(Tag.objects.all().values_list("slug", flat=True))
        return values

    def extract_value(self, request):
        value = request.REQUEST.getlist(self.request_name)
        if not value:
            return None
        return value

    def update_query(self, query, value):
        available_values = self.available_values

        if not isinstance(value, list):
            value = [value]

        if set(value) - set(available_values):
            raise Http404()

        if set(value) == set(available_values):
            return query

        return query.narrow(u"%s:(%s)" % (self.index_name, u" OR ".join(value)))

    def update_query_string_params(self, query_string_params, value):
        query_string_params[self.request_name] = value
        return query_string_params

    def page_subtitle(self, value):
        if isinstance(value, list):
            return "Keyword: %s" % u", ".join([(get_name_from_slug(Keyword, v) or get_name_from_slug(Tag, v)) for v in value])
        return "Keyword: %s" % (get_name_from_slug(Keyword, value) or get_name_from_slug(Tag, value))


class AlignmentFilter(Filter):

    def __init__(self, index_name, request_name):
        self.index_name = index_name
        self.request_name = request_name

    @property
    def available_values(self):
        values = set()
        for parts in TaggedMaterial.objects.all().values_list("tag__standard__code",
                                                              "tag__grade__code",
                                                              "tag__category__code",
                                                              "tag__code").order_by().distinct():
            values.add(".".join(parts))
        return values

    def extract_value(self, request):
        value = request.REQUEST.getlist(self.request_name)
        if not value:
            return None
        return value

    def update_query(self, query, value):
        available_values = self.available_values


        if not isinstance(value, list):
            value = [value]

        if set(value) - available_values:
            raise Http404()

        value = map(AlignmentTag.objects.get_from_full_code, value)

        return query.narrow(u"%s:(%s)" % (self.index_name, u" OR ".join([str(v.id) for v in value])))

    def update_query_string_params(self, query_string_params, value):
        query_string_params[self.request_name] = value
        return query_string_params

    def page_subtitle(self, value):
        if isinstance(value, list):
            return u"Alignment Tag: %s" % u", ".join(value)
        return u"Alignment Tag: %s" % value


class AlignmentClusterFilter(AlignmentFilter):

    def update_query(self, query, value):
        if not isinstance(value, list):
            value = [value]

        available_values = self.available_values

        if set(value) - available_values:
            raise Http404()

        tags = set()

        for code in value:
            tag = AlignmentTag.objects.get_from_full_code(code)
            tags.add(tag)
            for same_subcategory_tag in AlignmentTag.objects.filter(
                standard=tag.standard,
                grade=tag.grade,
                category=tag.category,
                subcategory=tag.subcategory):
                tags.add(same_subcategory_tag)

        return query.narrow(u"%s:(%s)" % (self.index_name, u" OR ".join([str(t.id) for t in tags])))

    def page_subtitle(self, value):
        if not isinstance(value, list):
            value = [value]
        clusters = set()
        for code in value:
            tag = AlignmentTag.objects.get_from_full_code(code)
            clusters.add(truncatechars(tag.subcategory, 90))
        return "Cluster: %s" % ",".join(sorted(clusters))


class AlignmentStandardFilter(AlignmentFilter):

    @property
    def available_values(self):
        return set(TaggedMaterial.objects.all().values_list("tag__standard__id", flat=True).order_by().distinct())

    def extract_value(self, request):
        value = request.REQUEST.getlist(self.request_name)
        if not value:
            return None
        value_ = []
        for v in value:
            try:
                v = int(v)
            except (TypeError, ValueError):
                continue
            value_.append(v)
        if not value_:
            return None
        return value_

    def update_query(self, query, value):
        if not isinstance(value, list):
            value = [value]

        available_values = self.available_values

        if set(value) - available_values:
            raise Http404()

        return query.narrow(u"%s:(%s)" % (self.index_name, u" OR ".join(map(str, value))))

    def page_subtitle(self, value):
        if not isinstance(value, list):
            value = [value]
        return ",".join([Standard.objects.get(id=id).name for id in value])


class AlignmentGradeFilter(AlignmentStandardFilter):

    def extract_value(self, request):
        value = request.REQUEST.getlist(self.request_name)
        if not value:
            return None
        return value

    @property
    def available_values(self):
        grades = set()
        for grade, end_grade in TaggedMaterial.objects.all().values_list("tag__grade__code", "tag__end_grade__code").order_by().distinct():
            grades.add("%s-%s" % (grade, end_grade) if end_grade else grade)
        return grades

    def page_subtitle(self, value):
        if not isinstance(value, list):
            value = [value]
        return ",".join([u"%s Grades" % code if "-" in code else unicode(Grade.objects.get(code=code)) for code in value])


class AlignmentCategoryFilter(AlignmentStandardFilter):

    @property
    def available_values(self):
        return set(TaggedMaterial.objects.all().values_list("tag__category__id", flat=True).order_by().distinct())

    def page_subtitle(self, value):
        if not isinstance(value, list):
            value = [value]
        return ",".join([unicode(LearningObjectiveCategory.objects.get(id=id)) for id in value])


class SearchParameters(object):

    EXACT_PHRASES_RE = re.compile(r'"[\s]*([^"]+?)[\s]*"', re.I | re.U)
    ANY_WORDS_RE = re.compile(r"\(([^\(]+? or [^\)]+?)\)", re.I | re.U)

    def __init__(self, **kwargs):

        self.all_words = kwargs.get("all_words", [])
        self.any_words = kwargs.get("any_words", [])
        self.exclude_words = kwargs.get("exclude_words", [])
        self.exact_phrases = kwargs.get("exact_phrases", [])

        raw_query = kwargs.get("raw_query", u"")

        if raw_query:
            self.exact_phrases += self.EXACT_PHRASES_RE.findall(raw_query)
            raw_query = self.EXACT_PHRASES_RE.sub(u" ", raw_query).replace('"', " ")

            for any_words_substring in self.ANY_WORDS_RE.findall(raw_query):
                for word in any_words_substring.split():
                    if word.lower() != "or" and word not in self.any_words:
                        self.any_words.append(word)

            raw_query = self.ANY_WORDS_RE.sub(u" ", raw_query).replace('(', " ").replace(')', " ")

            for word in raw_query.split():
                if word.startswith("-"):
                    word = word.lstrip("-")
                    if word:
                        self.exclude_words.append(word)
                else:
                    self.all_words.append(word)

        if len(self.any_words) == 1:
            if self.any_words[0] not in self.all_words:
                self.all_words.append(self.any_words[0])
            self.any_words = []

        self.all_words = [w for w in self.all_words if w.lower() != "and"]

    def __nonzero__(self):
        return bool(self.all_words or self.any_words or self.exclude_words or self.exact_phrases)

    def __unicode__(self):
        parts = []
        parts += self.all_words

        parts += [u'"%s"' % phrase for phrase in self.exact_phrases]

        if self.any_words:
            parts.append("(%s)" % " OR ".join(self.any_words))

        parts += [u"-%s" % w for w in self.exclude_words]

        return u" ".join(parts)

    def __str__(self):
        return unicode(self).encode("utf-8")


class SearchFilter(Filter):

    weighted_fields = ["title", "abstract", "keywords_names",
                       "collection_name", "institution_name", "authors"]

    request_name = "f.search"

    def extract_value(self, request):
        any_words = request.REQUEST.get("f.search.any", u"").split()
        exclude_words = request.REQUEST.get("f.search.exclude", u"").split()
        exact_phrases = request.REQUEST.get("f.search.exact", u"").replace(u'"', u"").strip()
        exact_phrases = exact_phrases and [exact_phrases] or []
        value = SearchParameters(raw_query=request.REQUEST.get("f.search", u""),
                                 any_words=any_words,
                                 exclude_words=exclude_words,
                                 exact_phrases=exact_phrases)
        if not value:
            return None
        return value

    def escape(self, value):
        if isinstance(value, (list, tuple)):
            return [self.escape(v) for v in value]
        return value.replace(u":", "\:").replace("!", "\!")

    def update_query(self, query, value):

        all_words = list(value.all_words)
        if not all_words:
            for phrase in value.exact_phrases:
                for word in phrase.split():
                    if word not in all_words:
                        all_words.append(word)

        if all_words or value.any_words:
            for field in self.weighted_fields:
                query = query.filter_or(**{"%s__in" % field:self.escape((all_words + value.any_words))})

        for phrase in value.exact_phrases:
            if " " not in phrase:
                query = query.filter(text_exact=u'"%s"' % self.escape(phrase))
            else:
                query = query.filter(text_exact=self.escape(phrase))

        for word in value.exclude_words:
            query = query.exclude(text_exact=self.escape(word))

        if value.any_words:
            query = query.filter(text_exact__in=self.escape(value.any_words))

        for word in all_words:
            query = query.filter(text=self.escape(word))

        return query

    def update_query_string_params(self, query_string_params, value):
        query_string_params["f.search"] = str(value)
        return query_string_params

    def page_subtitle(self, value):
        return unicode(value)


class RubricFilter(ChoicesFilter):

    def extract_value(self, request):
        value = super(RubricFilter, self).extract_value(request)
        if value is not None:
            try:
                value = map(int, value)
            except (TypeError, ValueError):
                raise Http404()
        return value


FILTERS = OrderedDict([
    ("general_subjects", VocabularyFilter("general_subjects", "f.general_subject", GeneralSubject, u"Subject Area")),
    ("grade_levels", VocabularyFilter("grade_levels", "f.edu_level", GradeLevel, u"Grade Level")),
    ("course_material_types", VocabularyFilter("course_material_types", "f.material_types", CourseMaterialType, u"Material Type")),
    ("library_material_types", VocabularyFilter("library_material_types", "f.lib_material_types", LibraryMaterialType, u"Material Type")),
    ("media_formats", VocabularyFilter("media_formats", "f.media_formats", MediaFormat, u"Media Format")),
    ("languages", VocabularyFilter("languages", "f.language", Language, u"Language")),
    ("geographic_relevance", VocabularyFilter("geographic_relevance", "f.geographic_relevance", GeographicRelevance, u"Intended Regional Relevance")),
    ("community_types", VocabularyFilter("community_types", "f.oer_type", CommunityType, u"OER Community Type")),
    ("community_topics", VocabularyFilter("community_topics", "f.oer_topic", CommunityTopic, u"OER Community Topic")),
    ("course_or_module", ChoicesFilter("course_or_module", "f.course_or_module", COURSE_OR_MODULE, u"Course Type")),
    ("cou_bucket", ChoicesFilter("cou_bucket", "f.cou_bucket", COU_BUCKETS, u"Conditions of Use")),
    ("license_type", ChoicesFilter("license", "f.license", LICENSE_TYPES, u"Conditions of Use")),
    ("member_activities", ChoicesFilter("member_activities", "f.member_activity", MEMBER_ACTIVITY_TYPES, u"Member Activity")),
    ("collection", VocabularyFilter("collection", "f.collection", Collection, u"Collection")),
    ("keywords", KeywordFilter("keywords", "f.keyword")),
    ("microsite", VocabularyFilter("microsites", "f.microsite", Microsite, u"Topic", ignore_all_values=False)),
    ("topics", VocabularyFilter("indexed_topics", "f.subtopic", Topic, u"SubTopic")),
    ("featured", BooleanFilter("featured", "f.featured", u"Featured Resources")),
    ("alignment", AlignmentFilter("alignment_tags", "f.alignment")),
    ("alignment_standards", AlignmentStandardFilter("alignment_standards", "f.alignment_standard")),
    ("alignment_grades", AlignmentGradeFilter("alignment_grades", "f.alignment_grade")),
    ("alignment_categories", AlignmentCategoryFilter("alignment_categories", "f.alignment_category")),
    ("alignment_cluster", AlignmentClusterFilter("alignment_tags", "f.cluster")),
    ("evaluated_rubrics", RubricFilter("evaluated_rubrics", "f.rubric", get_rubric_choices(), u"Rubric")),
    ("search", SearchFilter()),
])

