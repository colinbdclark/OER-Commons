from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django import forms
from geo.models import Country
from materials.models import GeneralSubject, GradeLevel, CourseMaterialType,\
    MediaFormat, Language, GeographicRelevance, LibraryMaterialType, Course,\
    Library
from materials.models.course import COURSE_OR_MODULE
from project.utils import slugify
import chardet
import csv
import datetime
import os
import re
import time
import zipfile


def force_list(value):
    if not isinstance(value, list):
        value = [value]
    return value


def force_unicode(value):
    def to_unicode(v):
        if not v:
            return u''
        if not isinstance(v, unicode):
            try:
                v = unicode(v, 'utf-8')
            except UnicodeDecodeError:
                encoding = chardet.detect(v)["encoding"]
                v = v.decode(encoding)
        return v

    if isinstance(value, (int, float)):
        value = unicode(value)
    elif isinstance(value, (list, tuple, set)):
        t = type(value)
        value = t([to_unicode(v) for v in value])
    else:
        value = to_unicode(value)
    return value


def smart_title_case(string):
    # Convert string to titlecase with respect to abbrevitations
    # Remove double spaces
    ALWAYS_LOWERCASE = ('a', 'of', 'if', 'the')

    words = string.split()
    for i, w in enumerate(words):
        if len(w) == 1:
            # single character, keep as is
            continue
        elif i > 0 and w.lower() in ALWAYS_LOWERCASE:
            # Word which always should be in lowercase if not the first word
            # in the sentence
            words[i] = w.lower()
        else:
            # Check for abbrebiation
            # Abbreviation is a word which contains an uppercase character
            # and this character is not the first one
            # Examples: IBM, eBay, WiFi
            abbr = False
            for c in w[1:]:
                if c.isupper():
                    abbr = True
                    break
            if abbr:
                # Abbrevitation, skip this word
                continue
                # Ok, we have a word which we can capitalize
            words[i] = w.capitalize()

    return " ".join(words)


def extract_string(s):
    if not isinstance(s, basestring):
        return u''
    return force_unicode(s.strip())


def extract_string_slugify(s):
    return force_unicode(slugify(extract_string(s)))


def extract_list(s):
    if not isinstance(s, basestring):
        return []
    return [force_unicode(v.strip()) for v in s.split('|') if v.strip()]


def extract_list_slugify(s):
    return [force_unicode(slugify(v)) for v in extract_list(s)]


def extract_boolean(s):
    return s == u'Yes'


def extract_date(s):
    if not isinstance(s, basestring):
        return None
    raw_date = s.strip()
    if not raw_date:
        return None
    if re.match(r"^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}$", raw_date):
        t = time.mktime(time.strptime(raw_date, '%Y/%m/%d'))
    elif re.match(r"^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}$", raw_date):
        t = time.mktime(time.strptime(raw_date, '%Y-%m-%d'))
    elif re.match(r"^[0-9]{1,2}-[0-9]{1,2}-[0-9]{4}$", raw_date):
        t = time.mktime(time.strptime(raw_date, '%m-%d-%Y'))
    elif re.match(
        r"^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}T[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}Z$",
        raw_date):
        t = time.mktime(time.strptime(raw_date, '%Y-%m-%dT%H:%M:%SZ'))
    elif re.match(r"^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$", raw_date):
        t = time.mktime(time.strptime(raw_date, '%d/%m/%Y'))
    elif len(raw_date.split()) == 6:
        # Assume that date is in "Tue Nov 13 11:00:00 -0500 2007" format
        l = raw_date.split()
        d = " ".join((l[1], l[2], l[5]))
        t = time.mktime(time.strptime(d, '%b %d %Y'))
    else:
        raise ValidationError('Invalid date: %s' % raw_date)
    return datetime.date.fromtimestamp(t)


def extract_keywords(value):
    keywords = extract_list(value)
    return sorted(set([smart_title_case(k) for k in keywords]))

URL_VALIDATOR = URLValidator()

def check_URL(value):
    errors = []
    if value:
        try:
            URL_VALIDATOR(value)
        except ValidationError:
            errors.append(u"Invalid URL: %s" % value)
    return errors


def check_required(value):
    errors = []
    if not value:
        errors.append(u"Missing value")
    return errors


def check_in_list(available_values):
    assert isinstance(available_values, set)

    def check(values):
        errors = []
        if not values:
            values = set()
        elif not isinstance(values, (list, set, tuple)):
            values = set([values])
        for invalid_value in set(values) - available_values:
            errors.append("Invalid value: %s" % invalid_value)
        return errors

    return check

COUNTRY_SLUGS = set(Country.objects.all().values_list("slug", flat=True))
GENERAL_SUBJECT_SLUGS = set(
    GeneralSubject.objects.all().values_list("slug", flat=True))
GRADE_LEVEL_SLUGS = set(
    GradeLevel.objects.all().values_list("slug", flat=True))
COURSE_MATERIAL_TYPE_SLUGS = set(
    CourseMaterialType.objects.all().values_list("slug", flat=True))
LIBRARY_MATERIAL_TYPE_SLUGS = set(
    LibraryMaterialType.objects.all().values_list("slug", flat=True))
MEDIA_FORMAT_SLUGS = set(
    MediaFormat.objects.all().values_list("slug", flat=True))
LANGUAGE_SLUGS = set(Language.objects.all().values_list("slug", flat=True))
GEO_RELEVANCE_SLUGS = set(
    GeographicRelevance.objects.all().values_list("slug", flat=True))

COURSE_FIELDS = {
    'CR_SHORT_NAME': (extract_string, None),
    'CR_ID': (extract_string, None),
    'CR_NATIVE_ID': (extract_string, None),
    'CR_COURSE_ID': (extract_string, None),
    'CR_TITLE': (extract_string, check_required),
    'CR_FCOLM': (extract_string_slugify, check_in_list(set(dict(COURSE_OR_MODULE).keys()))),
    'CR_CREATE_DATE': (extract_date, None),
    'CR_ENTRY_DATE': (lambda x: None, None),
    'CR_AUTHOR_NAME': (extract_list, None),
    'CR_AUTHOR_EMAIL': (extract_list, None),
    'CR_AUTHOR_COUNTRY': (extract_list_slugify, check_in_list(COUNTRY_SLUGS)),
    'CR_INSTITUTION': (extract_string, check_required),
    'CR_URL': (extract_string, [check_required, check_URL]),
    'CR_NEW_URL': (extract_string, [check_URL]),
    'CR_IS_PART_OF_OCW': (extract_boolean, None),
    'CR_COLLECTION': (extract_string, check_required),
    'CR_SUBJECT': (extract_list_slugify, [check_required, check_in_list(GENERAL_SUBJECT_SLUGS)]),
    'CR_MATERIAL_TYPE': (extract_list_slugify, [check_required, check_in_list(COURSE_MATERIAL_TYPE_SLUGS)]),
    'CR_MEDIA_FORMATS': (extract_list_slugify, [check_required, check_in_list(MEDIA_FORMAT_SLUGS)]),
    'CR_NOTABLE_REQS': (extract_string, None),
    'CR_LEVEL': (extract_list_slugify, [check_required, check_in_list(GRADE_LEVEL_SLUGS)]),
    'CR_ABSTRACT': (extract_string, check_required),
    'CR_KEYWORDS': (extract_keywords, check_required),
    'CR_LANGUAGE': (extract_list, check_in_list(LANGUAGE_SLUGS)),
    'CR_IRR': (extract_list_slugify, check_in_list(GEO_RELEVANCE_SLUGS)),
    'CR_PREREQ_TITLE1': (extract_string, None),
    'CR_PREREQ_URL1': (extract_string, check_URL),
    'CR_PREREQ_TITLE2': (extract_string, None),
    'CR_PREREQ_URL2': (extract_string, check_URL),
    'CR_POSTREQ_TITLE1': (extract_string, None),
    'CR_POSTREQ_URL1': (extract_string, check_URL),
    'CR_POSTREQ_TITLE2': (extract_string, None),
    'CR_POSTREQ_URL2': (extract_string, check_URL),
    'CR_COU_URL': (extract_string, check_URL),
    'CR_COU_TITLE': (extract_string, None),
    'CR_COU_DESCRIPTION': (extract_string, None),
    'CR_COU_COPYRIGHT_HOLDER': (extract_string, None),
    'CR_PARENT_MODIFIED': (extract_boolean, None),
    'CR_PARENT_TITLE': (extract_string, None),
    'CR_PARENT_URL': (extract_string, check_URL),
    'CR_PARENT_CHANGES': (extract_string, None),
    'CR_CKSUM': (extract_string, None),
    'CR_CURRIC_STANDARDS': (extract_string, None),
    'CR_LEVEL_NEW': (extract_string, None),
    'CR_SUBJECT_NEW': (extract_string, None),
    'CR_AUDIENCE': (extract_string, None),
    'CR_COU_BUCKET' : (extract_string, None),
}

LIBRARY_FIELDS = {
    'LIB_SHORT_NAME': (extract_string, None),
    'LIB_ID': (extract_string, None),
    'LIB_NATIVE_ID': (extract_string, None),
    'LIB_TITLE': (extract_string, check_required),
    'LIB_CREATE_DATE': (extract_date, None),
    'LIB_ENTRY_DATE': (lambda x: None, None),
    'LIB_AUTHOR_NAME': (extract_list, None),
    'LIB_AUTHOR_EMAIL': (extract_list, None),
    'LIB_AUTHOR_COUNTRY': (extract_list_slugify, check_in_list(COUNTRY_SLUGS)),
    'LIB_INSTITUTION': (extract_string, check_required),
    'LIB_URL': (extract_string, [check_required, check_URL]),
    'LIB_NEW_URL': (extract_string, [check_URL]),
    'LIB_COLLECTION': (extract_string, check_required),
    'LIB_SUBJECT': (extract_list_slugify, [check_required, check_in_list(GENERAL_SUBJECT_SLUGS)]),
    'LIB_MATERIAL_TYPE': (extract_list_slugify, [check_required, check_in_list(LIBRARY_MATERIAL_TYPE_SLUGS)]),
    'LIB_MEDIA_FORMATS': (extract_list_slugify, [check_required, check_in_list(MEDIA_FORMAT_SLUGS)]),
    'LIB_IS_HOME_PAGE': (extract_boolean, None),
    'LIB_NOTABLE_REQS': (extract_string, None),
    'LIB_LEVEL': (extract_list_slugify, [check_required, check_in_list(GRADE_LEVEL_SLUGS)]),
    'LIB_ABSTRACT': (extract_string, check_required),
    'LIB_KEYWORDS': (extract_keywords, check_required),
    'LIB_LANGUAGE': (extract_list, check_in_list(LANGUAGE_SLUGS)),
    'LIB_IRR': (extract_list_slugify, check_in_list(GEO_RELEVANCE_SLUGS)),
    'LIB_COU_URL': (extract_string, check_URL),
    'LIB_COU_TITLE': (extract_string, None),
    'LIB_COU_DESCRIPTION': (extract_string, None),
    'LIB_COU_COPYRIGHT_HOLDER': (extract_string, None),
    'LIB_CURRIC_STANDARDS': (extract_string, None),
    'LIB_LEVEL_NEW': (extract_string, None),
    'LIB_SUBJECT_NEW': (extract_string, None),
    'LIB_AUDIENCE': (extract_string, None),
    'LIB_COU_BUCKET' : (extract_string, None),
}


class ValidateCSVForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.validation_errors = []
        self.header = None
        self.fields_definition = None
        self.csv_data = []
        self.model = None
        self.filename = None
        super(ValidateCSVForm, self).__init__(*args, **kwargs)

    def add_validation_error(self, message, line_number=u"", field=u""):
        self.validation_errors.append((line_number, field, message))

    def clean_file(self):
        file = self.cleaned_data["file"]
        if file.content_type == "application/zip":
            try:
                zip = zipfile.ZipFile(file)
            except zipfile.BadZipfile:
                raise forms.ValidationError(
                    u"Can't open the archive. Make sure it is a valid ZIP "\
                    "file.")
            for zipinfo in zip.infolist():
                if zipinfo.filename.endswith(".csv"):
                    filename = os.path.split(zipinfo.filename)[-1]
                    self.filename = filename
                    file = InMemoryUploadedFile(
                        zip.open(zipinfo.filename, "rU"),
                        "file", filename, "text/csv",
                        zipinfo.file_size, None)
                    break
            else:
                raise forms.ValidationError(
                    u"Can't find a CSV file in this archive.")
        else:
            self.filename = file.name
        if file.content_type != "text/csv":
            raise forms.ValidationError(
                u"This file does not appear to be a valid CSV file.")
        reader = csv.reader(file.file.read().splitlines())
        self.header = reader.next()
        self.header = map(lambda x: x.strip().upper(), self.header)
        if self.header[0].startswith("CR_"):
            self.fields_definition = COURSE_FIELDS
            self.model = Course
        elif self.header[0].startswith("LIB_"):
            self.fields_definition = LIBRARY_FIELDS
            self.model = Library
        else:
            raise forms.ValidationError(
                u"Can't find OER data in this CSV file.")

        for line_index, row in enumerate(reader):
            line_number = line_index + 2
            extracted_data = []
            for field_index, raw_value in enumerate(row):
                field_name = self.header[field_index]
                if field_name not in self.fields_definition:
                    self.add_validation_error("Uknown field", line_number,
                                              field_name)
                    continue

                extractor, validators = self.fields_definition[field_name]
                try:
                    value = extractor(raw_value)
                except ValidationError:
                    self.add_validation_error(
                        u"Can't extract value: %s" % raw_value,
                        line_number, field_name)
                    continue

                if validators:
                    if not isinstance(validators, (list, tuple)):
                        validators = [validators]
                    for validator in validators:
                        errors = validator(value)
                        if errors:
                            for error in errors:
                                self.add_validation_error(error, line_number,
                                                          field_name)

                extracted_data.append(value)

            if len(extracted_data) == len(row):
                self.csv_data.append(extracted_data)

        return file
