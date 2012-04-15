from common.models import GradeLevel, Grade, GradeSubLevel, MediaFormat
from core.search import reindex
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from geo.models import Country
from materials.models import Course, Library, GeneralSubject,\
    Language, GeographicRelevance, CourseMaterialType, \
    LibraryMaterialType, License
from materials.models.common import CC_LICENSE_URL_RE, PUBLIC_DOMAIN_URL_RE, GNU_FDL_URL_RE, PUBLIC_DOMAIN_NAME, GNU_FDL_NAME
from materials.models.material import IMPORTED_STATE
from materials.views.validate_csv import ValidateCSVForm
from utils.decorators import login_required
import sys


SIMPLE_FIELDS = [
    ("TITLE", "title"),
    ("SHORT_NAME", "slug"),
    ("ABSTRACT", "abstract"),
    ("CREATE_DATE", "content_creation_date"),
    ("NOTABLE_REQS", "tech_requirements"),
    ("CURRIC_STANDARDS", "curriculum_standards"),
    ("LEVEL_NEW", "new_level"),
    ("SUBJECT_NEW", "new_subject"),
    ("AUDIENCE", "audience"),
]

COURSE_SIMPLE_FIELDS = [
    ("COURSE_ID", "course_id"),
    ("NATIVE_ID", "provider_id"),
    ("FCOLM", "course_or_module"),
]

LIBRARY_SIMPLE_FIELDS = [
    ("IS_HOME_PAGE", "is_homepage"),
]

M2M_FIELDS = [
    ("SUBJECT", "general_subjects", GeneralSubject, "slug"),
    ("LEVEL", "grade_levels", GradeLevel, "slug"),
    ("SUBLEVEL", "grade_sublevels", GradeSubLevel, "slug"),
    ("GRADE", "grades", Grade, "code"),
    ("LANGUAGE", "languages", Language, "slug"),
    ("IRR", "geographic_relevance", GeographicRelevance, "slug"),
    ("MEDIA_FORMATS", "media_formats", MediaFormat, "slug"),
]

COURSE_M2M_FIELDS = [
    ("MATERIAL_TYPE", "material_types", CourseMaterialType, "slug"),
]

LIBRARY_M2M_FIELDS = [
    ("MATERIAL_TYPE", "material_types", LibraryMaterialType, "slug"),
]

class DataImport(TemplateView):

    template_name = "materials/data-import.html"

    @method_decorator(login_required)
    @method_decorator(transaction.commit_manually)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff and not request.user.is_superuser:
            return HttpResponseForbidden()
        self.form = None
        self.validation_errors = []
        return super(DataImport, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.form:
            self.form = ValidateCSVForm()
        return super(DataImport, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = ValidateCSVForm(request.POST, request.FILES)

        if not self.form.is_valid():
            messages.error(request, u"Data is not valid, see below.")
            return self.get(request, *args, **kwargs)

        if self.form.validation_errors:
            self.validation_errors = self.form.validation_errors
            messages.error(request, u"Data is not valid, see below.")
            return self.get(request, *args, **kwargs)

        if "validate" in request.REQUEST:
            messages.success(request, u"Data appears to be valid.")
            return self.get(request, *args, **kwargs)


        model = self.form.model
        if model == Course:
            field_name_prefix = "CR_"
            simple_fields = SIMPLE_FIELDS + COURSE_SIMPLE_FIELDS
            m2m_fields = M2M_FIELDS + COURSE_M2M_FIELDS
        elif model == Library:
            field_name_prefix = "LIB_"
            simple_fields = SIMPLE_FIELDS + LIBRARY_SIMPLE_FIELDS
            m2m_fields = M2M_FIELDS + LIBRARY_M2M_FIELDS

        authors_field = None
        keywords_field = None
        for field in model._meta.many_to_many:
            if field.name == "authors":
                authors_field = field
            elif field.name == "keywords":
                keywords_field = field

        institution_field = None
        collection_field = None
        license_field = None
        prerequisite_1_field = None
        prerequisite_2_field = None
        postrequisite_1_field = None
        postrequisite_2_field = None
        derived_from_field = None
        for field in model._meta.fields:
            if field.name == "institution":
                institution_field = field
            elif field.name == "collection":
                collection_field = field
            elif field.name == "license":
                license_field = field
            elif field.name == "prerequisite_1":
                prerequisite_1_field = field
            elif field.name == "prerequisite_2":
                prerequisite_2_field = field
            elif field.name == "postrequisite_1":
                postrequisite_1_field = field
            elif field.name == "postrequisite_2":
                postrequisite_2_field = field
            elif field.name == "derived_from":
                derived_from_field = field


        imported_objects = []

        for row_index, row in enumerate(self.form.csv_data):

            data = {}

            for field_index, value in enumerate(row):
                field_name = self.form.header[field_index][len(field_name_prefix):]
                data[field_name] = value

            try:
                check_for_unique_url = True
                try:
                    obj = model.objects.get(url=data["URL"])
                    new_url = data.get("NEW_URL")
                    if new_url:
                        obj.url = new_url
                    else:
                        check_for_unique_url = False
                except MultipleObjectsReturned:
                    self.validation_errors.append(
                        (row_index + 1, u"", u"URL '%s' is registered multiple times, can't find an object to update." % data["URL"])
                    )
                    continue
                except model.DoesNotExist:
                    obj = model(creator=request.user)
                    obj.url = data["URL"]
                    obj.workflow_state = IMPORTED_STATE

                # Do not re-index the object until the transaction is finished
                obj.skip_indexing = True

                if check_for_unique_url and model.objects.filter(url=obj.url).exists():
                    self.validation_errors.append(
                        (row_index + 1, u"", u"URL '%s' is registered in database already." % obj.url)
                    )
                    continue

                for csv_field_name, obj_field_name in simple_fields:
                    if csv_field_name in data:
                        setattr(obj, obj_field_name, data[csv_field_name])

                if institution_field and "INSTITUTION" in data:
                    institution_field.save_form_data(obj, dict(name=data["INSTITUTION"]))

                if collection_field and "COLLECTION" in data:
                    collection_field.save_form_data(obj, dict(name=data["COLLECTION"]))

                if license_field and ("COU_TITLE" in data or "COU_URL" in data):
                    url = data.get("COU_URL", u"")
                    name = data.get("COU_TITLE", u"")
                    if url:
                        if CC_LICENSE_URL_RE.match(url):
                            name = License.objects.get_cc_license_name_from_url(url)
                        elif PUBLIC_DOMAIN_URL_RE.match(url):
                            name = PUBLIC_DOMAIN_NAME
                        elif GNU_FDL_URL_RE.match(url):
                            name = GNU_FDL_NAME
                    description = data.get("COU_DESCRIPTION", u"")
                    copyright_holder = data.get("COU_COPYRIGHT_HOLDER", u"")
                    license_field.save_form_data(obj,
                        dict(url=url, name=name, description=description,
                             copyright_holder=copyright_holder)
                    )

                if prerequisite_1_field and "PREREQ_TITLE1" in data:
                    title = data["PREREQ_TITLE1"]
                    if title:
                        url = data.get("PREREQ_URL1", u"")
                        prerequisite_1_field.save_form_data(obj,
                            dict(title=title, url=url)
                        )
                    else:
                        obj.prerequisite_1 = None

                if prerequisite_2_field and "PREREQ_TITLE2" in data:
                    title = data["PREREQ_TITLE2"]
                    if title:
                        url = data.get("PREREQ_URL2", u"")
                        prerequisite_2_field.save_form_data(obj,
                            dict(title=title, url=url)
                        )
                    else:
                        obj.prerequisite_2 = None

                if postrequisite_1_field and "POSTREQ_TITLE1" in data:
                    title = data["POSTREQ_TITLE1"]
                    if title:
                        url = data.get("POSTREQ_URL1", u"")
                        postrequisite_1_field.save_form_data(obj,
                            dict(title=title, url=url)
                        )
                    else:
                        obj.postrequisite_1 = None

                if postrequisite_2_field and "POSTREQ_TITLE2" in data:
                    title = data["POSTREQ_TITLE2"]
                    if title:
                        url = data.get("POSTREQ_URL2", u"")
                        postrequisite_2_field.save_form_data(obj,
                            dict(title=title, url=url)
                        )
                    else:
                        obj.postrequisite_2 = None

                if derived_from_field:
                    if data.get("PARENT_MODIFIED") == False:
                        obj.derived_from = None
                    else:
                        title = data.get("PARENT_TITLE", u"")
                        if not title:
                            obj.derived_from = None
                        else:
                            url = data.get("PARENT_URL", u"")
                            description = data.get("PARENT_CHANGES", u"")
                            derived_from_field.save_form_data(obj,
                                dict(title=title, url=url, description=description)
                            )

                typical_age_range = data.get("TYPICAL_AGE_RANGE")
                if typical_age_range:
                    obj.start_age = typical_age_range[0]
                    obj.end_age = typical_age_range[1]

                obj.save()

                for csv_field_name, obj_field_name, field_model, field_model_key in m2m_fields:
                    if csv_field_name in data:
                        field = getattr(obj, obj_field_name)
                        field.clear()
                        for value in data[csv_field_name]:
                            field.add(field_model.objects.get(**{field_model_key: value}))

                if authors_field and "AUTHOR_NAME" in data:
                    author_names = data["AUTHOR_NAME"]
                    author_emails = data.get("AUTHOR_EMAIL", [])
                    author_countries = data.get("AUTHOR_COUNTRY", [])
                    obj.authors.clear()
                    authors_data = []
                    for i, name in enumerate(author_names):
                        try:
                            email = author_emails[i]
                        except IndexError:
                            email = u""
                        try:
                            country = Country.objects.get(slug=author_countries[i])
                        except IndexError:
                            country = None
                        authors_data.append(dict(name=name, email=email,
                                                 country=country))
                    authors_field.save_form_data(obj, authors_data)

                if keywords_field and "KEYWORDS" in data:
                    obj.keywords.clear()
                    keywords_data = []
                    for name in data["KEYWORDS"]:
                        keywords_data.append(dict(name=name))
                    keywords_field.save_form_data(obj, keywords_data)

                imported_objects.append(obj)

            except:
                transaction.rollback()
                if settings.DEBUG:
                    raise
                self.validation_errors.append(
                    (row_index + 1, u"", unicode(sys.exc_info()[1]))
                )

        if self.validation_errors:
            transaction.rollback()
            self.is_valid = False
            messages.error(request, u"There were some errors, see below.")
        else:
            if "dry_run" in request.REQUEST:
                transaction.rollback()
                messages.success(request, u"Data appears to be valid. "
                    "It is not imported because 'Dry run' option is selected.")
            else:
                transaction.commit()

                for object in imported_objects:
                    object.skip_indexing = False
                    reindex(object)

                transaction.commit()
                messages.success(request, u"Data was imported successfully.")

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(DataImport, self).get_context_data(**kwargs)
        data["form"] = self.form
        data["validation_errors"] = self.validation_errors
        data["page_title"] = u"Data Import"
        return data
