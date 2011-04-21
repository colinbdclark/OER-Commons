from StringIO import StringIO
from autoslug.settings import slugify
from django.http import Http404, HttpResponse
from materials.models.community import CommunityItem
from materials.models.course import COURSE_OR_MODULE, Course
from materials.models.library import Library
import csv


def process_date(value):
    if value is not None:
        return value.strftime("%Y-%m-%d")
    return ""


def process_course_or_module(value):
    if value:
        return unicode(dict(COURSE_OR_MODULE)[value])
    return ""


def process_author_names(value):
    return "|".join(value.values_list("name", flat=True))


def process_author_emails(value):
    return "|".join(value.values_list("email", flat=True))


def process_author_countries(value):
    return "|".join([v for v in value.values_list("country__name", flat=True) if v])


def process_boolean(value):
    if value is None:
        return ""
    return value and "Yes" or "No"


def process_vocabulary(value):
    return "|".join(value.values_list("name", flat=True))


def process_slugs(value):
    return "|".join(value.values_list("slug", flat=True))


class process_field_attr():

    def __init__(self, attr):
        self.attr = attr

    def __call__(self, value):
        if value is None:
            return ""
        return getattr(value, self.attr) or ""


COURSE_FIELDS = (
    ('CR_SHORT_NAME', "slug", None),
    ('CR_COURSE_ID', "course_id", None),
    ('CR_NATIVE_ID', "provider_id", None),
    ('CR_ENTRY_DATE', "published_on", process_date),
    ('CR_TITLE', "title", None),
    ('CR_FCOLM', "course_or_module", process_course_or_module),
    ('CR_CREATE_DATE', "content_creation_date", process_date),
    ('CR_AUTHOR_NAME', "authors", process_author_names),
    ('CR_AUTHOR_EMAIL', "authors", process_author_emails),
    ('CR_AUTHOR_COUNTRY', "authors", process_author_countries),
    ('CR_INSTITUTION', "institution", lambda x: x and x.name or ""),
    ('CR_URL', "url", None),
    ('CR_COLLECTION', "collection", lambda x: x and x.name or ""),
    ('CR_SUBJECT', "general_subjects", process_vocabulary),
    ('CR_MATERIAL_TYPE', "material_types", process_vocabulary),
    ('CR_MEDIA_FORMATS', "media_formats", process_vocabulary),
    ('CR_NOTABLE_REQS', "tech_requirements", None),
    ('CR_LEVEL', "grade_levels", process_vocabulary),
    ('CR_ABSTRACT', "abstract", None),
    ('CR_KEYWORDS', "keywords", process_vocabulary),
    ('CR_LANGUAGE', "languages", process_slugs),
    ('CR_IRR', "geographic_relevance", process_vocabulary),
    ('CR_PREREQ_TITLE1', "prerequisite_1", process_field_attr("title")),
    ('CR_PREREQ_URL1', "prerequisite_1", process_field_attr("url")),
    ('CR_PREREQ_TITLE2', "prerequisite_2", process_field_attr("title")),
    ('CR_PREREQ_URL2', "prerequisite_2", process_field_attr("url")),
    ('CR_POSTREQ_TITLE1', "postrequisite_1", process_field_attr("title")),
    ('CR_POSTREQ_URL1', "postrequisite_1", process_field_attr("url")),
    ('CR_POSTREQ_TITLE2', "postrequisite_2", process_field_attr("title")),
    ('CR_POSTREQ_URL2', "postrequisite_2", process_field_attr("url")),
    ('CR_COU_URL', "license", process_field_attr("url")),
    ('CR_COU_TITLE', "license", process_field_attr("name")),
    ('CR_COU_DESCRIPTION', "license", process_field_attr("description")),
    ('CR_COU_COPYRIGHT_HOLDER', "license", process_field_attr("copyright_holder")),
    ('CR_COU_BUCKET', "license", process_field_attr("bucket")),
    ('CR_PARENT_MODIFIED', "derived_from", lambda x: x and u"Yes" or u"No"),
    ('CR_PARENT_TITLE', "derived_from", process_field_attr("title")),
    ('CR_PARENT_URL', "derived_from", process_field_attr("url")),
    ('CR_PARENT_CHANGES', "derived_from", process_field_attr("description")),
    ('CR_CURRIC_STANDARDS', "curriculum_standards", None),
)

LIBRARY_FIELDS = (
    ('LIB_SHORT_NAME', "slug", None),
    ('LIB_NATIVE_ID', "provider_id", None),
    ('LIB_ENTRY_DATE', "published_on", process_date),
    ('LIB_TITLE', "title", None),
    ('LIB_CREATE_DATE', "content_creation_date", process_date),
    ('LIB_AUTHOR_NAME', "authors", process_author_names),
    ('LIB_AUTHOR_EMAIL', "authors", process_author_emails),
    ('LIB_AUTHOR_COUNTRY', "authors", process_author_countries),
    ('LIB_URL', "url", None),
    ('LIB_COLLECTION', "collection", lambda x: x and x.name or ""),
    ('LIB_IS_HOME_PAGE', "is_homepage", lambda x: x and 'Yes' or 'No'),
    ('LIB_INSTITUTION', "institution", lambda x: x and x.name or ""),
    ('LIB_LEVEL', "grade_levels", process_vocabulary),
    ('LIB_ABSTRACT', "abstract", None),
    ('LIB_SUBJECT', "general_subjects", process_vocabulary),
    ('LIB_NOTABLE_REQS', "tech_requirements", None),
    ('LIB_KEYWORDS', "keywords", process_vocabulary),
    ('LIB_LANGUAGE', "languages", process_slugs),
    ('LIB_MEDIA_FORMATS', "media_formats", process_vocabulary),
    ('LIB_MATERIAL_TYPE', "material_types", process_vocabulary),
    ('LIB_IRR', "geographic_relevance", process_vocabulary),
    ('LIB_COU_URL', "license", process_field_attr("url")),
    ('LIB_COU_TITLE', "license", process_field_attr("name")),
    ('LIB_COU_DESCRIPTION', "license", process_field_attr("description")),
    ('LIB_COU_COPYRIGHT_HOLDER', "license", process_field_attr("copyright_holder")),
    ('LIB_COU_BUCKET', "license", process_field_attr("bucket")),
    ('LIB_CURRIC_STANDARDS', "curriculum_standards", None),
)

COMMUNITY_ITEM_FIELDS = (
    ('OER_SHORT_NAME', "slug", None),
    ('OER_ENTRY_DATE', "published_on", process_date),
    ('OER_TITLE', "title", None),
    ('OER_CREATE_DATE', "content_creation_date", process_date),
    ('OER_AUTHOR_NAME', "authors", process_author_names),
    ('OER_AUTHOR_EMAIL', "author", process_author_emails),
    ('OER_AUTHOR_COUNTRY', "author", process_author_countries),
    ('OER_URL', "url", None),
    ('OER_SUBJECT', "general_subjects", process_vocabulary),
    ('OER_NOTABLE_REQS', "tech_requirements", None),
    ('OER_LEVEL', "grade_levels", process_vocabulary),
    ('OER_ABSTRACT', "abstract", None),
    ('OER_KEYWORDS', "keywords", process_vocabulary),
    ('OER_LANGUAGE', "languages", process_slugs),
    ('OER_CONTENTTYPE', "community_types", process_vocabulary),
    ('OER_CONTENTTOPIC', "community_topics", process_vocabulary),
    ('OER_IRR', "geographic_relevance", process_vocabulary),
    ('OER_COU_URL', "license", process_field_attr("url")),
    ('OER_COU_TITLE', "license", process_field_attr("name")),
    ('OER_COU_DESCRIPTION', "license", process_field_attr("description")),
    ('OER_COU_COPYRIGHT_HOLDER', "license", process_field_attr("copyright_holder")),
    ('OER_COU_BUCKET', "license", process_field_attr("bucket")),
)


def csv_export(query, title):
    query.load_all()

    has_courses = False
    has_libraries = False
    has_community_items = False
    model = None

    for result in query:
        if result.model == Course:
            has_courses = True
        elif result.model == Library:
            has_libraries = True
        elif result.model == CommunityItem:
            has_community_items = True
        if has_courses and has_libraries and has_community_items:
            break

    if has_courses:
        fields = COURSE_FIELDS
        model = Course
    elif has_libraries:
        fields = LIBRARY_FIELDS
        model = Library
    elif has_community_items:
        fields = COMMUNITY_ITEM_FIELDS
        model = CommunityItem
    else:
        raise Http404()

    out = StringIO()
    writer = csv.writer(out, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([f[0] for f in fields])

    for result in query:
        if result.model != model:
            continue
        row = []
        object = result.object
        for field_name, attr_name, processor in fields:
            attr_value = getattr(object, attr_name)
            if not attr_value:
                row.append("")
            if processor is not None:
                attr_value = processor(attr_value)
            if not attr_value:
                row.append("")
            if isinstance(attr_value, unicode):
                attr_value = attr_value.encode("utf-8")
            row.append(attr_value)
        writer.writerow(row)

    title = slugify(title)
    if not title:
        title = 'export'

    out.seek(0)
    response = HttpResponse(out.read(), content_type="text/csv")
    response['Content-Disposition'] = 'inline;filename="%s.csv"' % title
    return response
