from config import items_vocabularies

import csv, sys, re, time, string, random, datetime, urllib
import chardet


CC_LICENSE_URL_RE = 'http://(www\.)?creativecommons\.org/licenses/(by|by-sa|by-nd|by-nc|by-nc-sa|by-nc-nd|nc-sa)/[0-9]\.[0-9]'
PUBLIC_DOMAIN_URL = u"http://creativecommons.org/licenses/publicdomain/"
GNU_FDL_URL = u"http://www.gnu.org/licenses/fdl.txt"

vocabularies_as_dict = {}

for key, value in items_vocabularies.items():
    voc = {}
    for k, v in value:
        voc[v] = k
    vocabularies_as_dict[key] = voc

COURSE_TYPE = 'course'
LIBRARY_TYPE = 'library'

# UnicodeData.txt does not contain normalization of Greek letters.
mapping_greek = {
912: 'i', 913: 'A', 914: 'B', 915: 'G', 916: 'D', 917: 'E', 918: 'Z',
919: 'I', 920: 'TH', 921: 'I', 922: 'K', 923: 'L', 924: 'M', 925: 'N',
926: 'KS', 927: 'O', 928: 'P', 929: 'R', 931: 'S', 932: 'T', 933: 'Y',
934: 'F', 936: 'PS', 937: 'O', 938: 'I', 939: 'Y', 940: 'a', 941: 'e',
943: 'i', 944: 'y', 945: 'a', 946: 'b', 947: 'g', 948: 'd', 949: 'e',
950: 'z', 951: 'i', 952: 'th', 953: 'i', 954: 'k', 955: 'l', 956: 'm',
957: 'n', 958: 'ks', 959: 'o', 960: 'p', 961: 'r', 962: 's', 963: 's',
964: 't', 965: 'y', 966: 'f', 968: 'ps', 969: 'o', 970: 'i', 971: 'y',
972: 'o', 973: 'y' }

# Russian character mapping thanks to Xenru.
mapping_russian = {
1081 : 'i', 1049 : 'I', 1094 : 'c', 1062 : 'C',
1091 : 'u', 1059 : 'U', 1082 : 'k', 1050 : 'K',
1077 : 'e', 1045 : 'E', 1085 : 'n', 1053 : 'N',
1075 : 'g', 1043 : 'G', 1096 : 'sh', 1064 : 'SH',
1097 : 'sch', 1065 : 'SCH', 1079 : 'z', 1047 : 'Z',
1093 : 'h', 1061 : 'H', 1098 : '', 1066 : '',
1092 : 'f', 1060 : 'F', 1099 : 'y', 1067 : 'Y',
1074 : 'v', 1042 : 'V', 1072 : 'a', 1040 : 'A',
1087 : 'p', 1055 : 'P', 1088 : 'r', 1056 : 'R',
1086 : 'o', 1054 : 'O', 1083 : 'l', 1051 : 'L',
1076 : 'd', 1044 : 'D', 1078 : 'zh', 1046 : 'ZH',
1101 : 'e', 1069 : 'E', 1103 : 'ya', 1071 : 'YA',
1095 : 'ch', 1063 : 'CH', 1089 : 's', 1057 : 'S',
1084 : 'm', 1052 : 'M', 1080 : 'i', 1048 : 'I',
1090 : 't', 1058 : 'T', 1100 : '', 1068 : '',
1073 : 'b', 1041 : 'B', 1102 : 'yu', 1070 : 'YU',
1105 : 'yo', 1025 : 'YO' }

# Turkish character mapping.
mapping_turkish = {
286 : 'G', 287 : 'g', 304 : 'I', 305 : 'i', 350 : 'S', 351 : 's' }

# Latin characters with accents, etc.
mapping_latin_chars = {
138 : 's', 140 : 'O', 142 : 'z', 154 : 's', 156 : 'o', 158 : 'z', 159 : 'Y',
192 : 'A', 193 : 'A', 194 : 'A', 195 : 'a', 196 : 'A', 197 : 'A', 198 : 'E',
199 : 'C', 200 : 'E', 201 : 'E', 202 : 'E', 203 : 'E', 204 : 'I', 205 : 'I',
206 : 'I', 207 : 'I', 208 : 'D', 209 : 'N', 210 : 'O', 211 : 'O', 212 : 'O',
213 : 'O', 214 : 'O', 215 : 'x', 216 : 'O', 217 : 'U', 218 : 'U', 219 : 'U',
220 : 'U', 221 : 'Y', 223 : 's', 224 : 'a', 225 : 'a', 226 : 'a', 227 : 'a',
228 : 'a', 229 : 'a', 230 : 'e', 231 : 'c', 232 : 'e', 233 : 'e', 234 : 'e',
235 : 'e', 236 : 'i', 237 : 'i', 238 : 'i', 239 : 'i', 240 : 'd', 241 : 'n',
242 : 'o', 243 : 'o', 244 : 'o', 245 : 'o', 246 : 'o', 248 : 'o', 249 : 'u',
250 : 'u', 251 : 'u', 252 : 'u', 253 : 'y', 255 : 'y' }

# Feel free to add new user-defined mapping. Don't forget to update mapping dict
# with your dict.
mapping = {}
mapping.update(mapping_greek)
mapping.update(mapping_russian)
mapping.update(mapping_latin_chars)
mapping.update(mapping_turkish)

# On OpenBSD string.whitespace has a non-standard implementation
# See http://dev.plone.org/plone/ticket/4704 for details
whitespace = ''.join([c for c in string.whitespace if ord(c) < 128])
allowed = string.ascii_letters + string.digits + string.punctuation + whitespace

def normalizeUnicode(text):
    """
    This method is used for normalization of unicode characters to the base ASCII
    letters. Output is ASCII encoded string (or char) with only ASCII letters,
    digits, punctuation and whitespace characters. Case is preserved.
    """
    if not isinstance(text, unicode):
        raise TypeError('must pass Unicode argument to normalizeUnicode()')

    res = ''
    for ch in text:
        if ch in allowed:
            # ASCII chars, digits etc. stay untouched
            res += ch
        else:
            ordinal = ord(ch)
            if mapping.has_key(ordinal):
                # try to apply custom mappings
                res += mapping.get(ordinal)
            elif unicodedata.decomposition(ch):
                normalized = unicodedata.normalize('NFKD', ch).strip()
                # normalized string may contain non-letter chars too. Remove them
                # normalized string may result to  more than one char
                res += ''.join([c for c in normalized if c in allowed])
            else:
                # hex string instead of unknown char
                res += "%x" % ordinal
    return res.encode('ascii')

# Define and compile static regexes
FILENAME_REGEX = re.compile(r"^(.+)\.(\w{,4})$")
NON_WORD_REGEX = re.compile(r"[\W\-]+")
DANGEROUS_CHARS_REGEX = re.compile(r"[?&/:\\#]+")
EXTRA_DASHES_REGEX = re.compile(r"(^\-+)|(\-+$)")

def normalizeString(text, encoding='utf-8', relaxed=False):

    # Make sure we are dealing with a unicode string
    if not isinstance(text, unicode):
        text = unicode(text, encoding)

    text = text.strip()
    if not relaxed:
        text = text.lower()
    text = normalizeUnicode(text)

    base = text
    ext  = ""

    m = FILENAME_REGEX.match(text)
    if m is not None:
        base = m.groups()[0]
        ext  = m.groups()[1]

    if not relaxed:
        base = NON_WORD_REGEX.sub("-", base)
    else:
        base = DANGEROUS_CHARS_REGEX.sub("-", base)

    base = EXTRA_DASHES_REGEX.sub("", base)

    if ext != "":
        base = base + "." + ext
    return base


class UniqueIDGenerator:

    _v_nextid = None

    _randrange = random.randrange

    def _generateId(self, used_ids):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, 2**31)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in used_ids:
                return uid
            self._v_nextid = None


def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


def force_list(value):
    if not isinstance(value, list):
        value = [value]
    return value

def force_unicode(value):
    def to_unicode(v):
        if not v:
            return u''
        if not isinstance(v, unicode):
            v = unicode(v, 'utf-8')
        return v
    if isinstance(value, (int, float)):
        value = unicode(value)
    elif isinstance(value, (list, tuple, set)):
        t = type(value)
        value = t([to_unicode(v) for v in value])
    else:
        value = to_unicode(value)
    return value


def smartTitleCase(string):
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


class ValidationError(Exception):
    pass


def extractString(s):
    if not isinstance(s, basestring):
        return u''
    return force_unicode(s.strip())

def extractStringNormalize(s):
    return force_unicode(normalizeString(extractString(s)))

def extractList(s):
    if not isinstance(s, basestring):
        return []
    return [force_unicode(v.strip()) for v in s.split('|') if v.strip()]

def extractListNormalize(s):
    return [force_unicode(normalizeString(v)) for v in extractList(s)]

def extractBoolean(s):
    return s == u'Yes'

def extractDate(s):
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
    elif re.match(r"^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}T[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}Z$", raw_date):
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

def checkRequired(value, data=None):
    if not value:
        raise ValidationError(u"Missing value")
    return value

def checkLicenseTitle(value, data):
    if data['license_url'] and (data['license_url'] in (PUBLIC_DOMAIN_URL, GNU_FDL_URL) or \
       re.match(CC_LICENSE_URL_RE, data['license_url'])):
        return value
    return checkRequired(value)

checkCOUBucket = checkLicenseTitle

def checkAgainstVocabulary(value, vocabularyName):
    vocabulary = vocabularies_as_dict[vocabularyName]
    if not value:
        return value
    if isinstance(value, list):
        for v in value:
            try:
                vocabulary[v]
            except KeyError:
                raise ValidationError(u"Invalid value: %s" % v)
    else:
        try:
            vocabulary[value]
        except KeyError:
            raise ValidationError(u"Invalid value: %s" % value)
    return value

def checkURL(value, data=None):
    if not value or value.startswith('http://') or \
        value.startswith('https://') or value.startswith('ftp://'):
        return value
    raise ValidationError(u"Invalid value: %s" % value)

def extractKeywords(value):
    keywords = extractList(value)
    return sorted(unique([smartTitleCase(k) for k in keywords]))

COURSE_FIELDS = {
  'CR_SHORT_NAME':(
       extractString, lambda x, y: x, 'name'),
  'CR_ID':(
       extractString, lambda x, y: x, 'iskme_id'),
  'CR_NATIVE_ID':(
      extractString, lambda x, y: x, 'native_id'),
  'CR_COURSE_ID':(
      extractString, lambda x, y: x, 'course_id'),
  'CR_TITLE':(
      extractString, checkRequired, 'title'),
  'CR_FCOLM':(
      extractStringNormalize, lambda x, y: checkAgainstVocabulary(x, 'course_or_module'), 'course_or_module'),
  'CR_CREATE_DATE':(
      extractDate, lambda x, y: x, 'content_creation_date'),
  'CR_ENTRY_DATE': (
      lambda x: None, lambda x, y: x, '_entry_date'),
  'CR_AUTHOR_NAME':(
      extractList, lambda x, y: x, 'authors'),
  'CR_AUTHOR_EMAIL':(
      extractList, lambda x, y: x, 'author_emails'),
  'CR_AUTHOR_COUNTRY':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(x, 'countries'), 'author_countries'),
  'CR_INSTITUTION':(
      extractString, lambda x, y: checkRequired(x), 'institution'),
  'CR_URL':(
      extractString, lambda x, y: checkURL(checkRequired(x)), 'remote_url'),
  'CR_IS_PART_OF_OCW':(
      extractBoolean, lambda x, y: x, 'is_ocw'),
  'CR_COLLECTION':(
      extractString, checkRequired, 'collection'),
  'CR_SUBJECT':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'general_subjects'), 'general_subjects'),
  'CR_MATERIAL_TYPE':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'material_types'), 'material_types'),
  'CR_MEDIA_FORMATS':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'media_formats'), 'media_formats'),
  'CR_NOTABLE_REQS':(
      extractString, lambda x, y: x, 'tech_requirements'),
  'CR_LEVEL':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'grade_levels'), 'grade_levels'),
  'CR_ABSTRACT':(
      extractString, checkRequired, 'description'),
  'CR_KEYWORDS':(
      extractKeywords, lambda x, y: checkRequired, 'keywords'),
  'CR_LANGUAGE':(
      extractList, lambda x, y: checkAgainstVocabulary(x, 'languages'), 'languages'),
  'CR_IRR':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(x, 'geographic_relevance'), 'geographic_relevance'),
  'CR_PREREQ_TITLE1':(
      extractString, lambda x, y: x, 'prerequisite_1_title'),
  'CR_PREREQ_URL1':(
      extractString, checkURL, 'prerequisite_1_url'),
  'CR_PREREQ_TITLE2':(
      extractString, lambda x, y: x, 'prerequisite_2_title'),
  'CR_PREREQ_URL2':(
      extractString, checkURL, 'prerequisite_2_url'),
  'CR_POSTREQ_TITLE1':(
      extractString, lambda x, y: x, 'postrequisite_1_title'),
  'CR_POSTREQ_URL1':(
      extractString, checkURL, 'postrequisite_1_url'),
  'CR_POSTREQ_TITLE2':(
      extractString, lambda x, y: x, 'postrequisite_2_title'),
  'CR_POSTREQ_URL2':(
      extractString, checkURL, 'postrequisite_2_url'),
  'CR_COU_URL':(
      extractString, checkURL, 'license_url'),
  'CR_COU_TITLE':(
      extractString, lambda x, y: checkLicenseTitle(x, y), 'license_name'),
  'CR_COU_DESCRIPTION':(
      extractString, lambda x, y: x, 'license_description'),
  'CR_COU_COPYRIGHT_HOLDER':(
      extractString, lambda x, y: x, 'copyright_holder'),
  'CR_COU_BUCKET':(
      extractStringNormalize, lambda x, y: checkAgainstVocabulary(checkCOUBucket(x, y), 'cou_buckets'), 'cou_bucket'),
  'CR_PARENT_MODIFIED':(
      extractBoolean, lambda x, y: x, 'is_derived'),
  'CR_PARENT_TITLE':(
      extractString, lambda x, y: x, 'derived_title'),
  'CR_PARENT_URL':(
      extractString, checkURL, 'derived_url'),
  'CR_PARENT_CHANGES':(
      extractString, lambda x, y: x, 'derived_why'),
  'CR_CKSUM':(
      extractString, lambda x, y: x, 'cksum'),
  'CR_CURRIC_STANDARDS':(
      extractString, lambda x, y: x, 'curriculum_standards'),
}

LIBRARY_FIELDS = {
  'LIB_SHORT_NAME':(
       extractString, lambda x, y: x, 'name'),
  'LIB_ID':(
       extractString, lambda x, y: x, 'iskme_id'),
  'LIB_NATIVE_ID':(
      extractString, lambda x, y: x, 'native_id'),
  'LIB_TITLE':(
      extractString, checkRequired, 'title'),
  'LIB_CREATE_DATE':(
      extractDate, lambda x, y: x, 'content_creation_date'),
  'LIB_ENTRY_DATE': (
      lambda x: None, lambda x, y: x, '_entry_date'),
  'LIB_AUTHOR_NAME':(
      extractList, lambda x, y: x, 'authors'),
  'LIB_AUTHOR_EMAIL':(
      extractList, lambda x, y: x, 'author_emails'),
  'LIB_AUTHOR_COUNTRY':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(x, 'countries'), 'author_countries'),
  'LIB_INSTITUTION':(
      extractString, lambda x, y: checkRequired(x), 'institution'),
  'LIB_URL':(
      extractString, lambda x, y: checkURL(checkRequired(x)), 'remote_url'),
  'LIB_COLLECTION':(
      extractString, checkRequired, 'collection'),
  'LIB_SUBJECT':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'general_subjects'), 'general_subjects'),
  'LIB_MATERIAL_TYPE':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'library_material_types'), 'material_types'),
  'LIB_MEDIA_FORMATS':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'media_formats'), 'media_formats'),
  'LIB_IS_HOME_PAGE':(
      extractBoolean, lambda x, y: x, 'is_homepage'),
  'LIB_NOTABLE_REQS':(
      extractString, lambda x, y: x, 'tech_requirements'),
  'LIB_LEVEL':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(checkRequired(x), 'grade_levels'), 'grade_levels'),
  'LIB_ABSTRACT':(
      extractString, checkRequired, 'description'),
  'LIB_KEYWORDS':(
      extractKeywords, lambda x, y: checkRequired, 'keywords'),
  'LIB_LANGUAGE':(
      extractList, lambda x, y: checkAgainstVocabulary(x, 'languages'), 'languages'),
  'LIB_IRR':(
      extractListNormalize, lambda x, y: checkAgainstVocabulary(x, 'geographic_relevance'), 'geographic_relevance'),
  'LIB_COU_URL':(
      extractString, checkURL, 'license_url'),
  'LIB_COU_TITLE':(
      extractString, lambda x, y: checkLicenseTitle(x, y), 'license_name'),
  'LIB_COU_DESCRIPTION':(
      extractString, lambda x, y: x, 'license_description'),
  'LIB_COU_COPYRIGHT_HOLDER':(
      extractString, lambda x, y: x, 'copyright_holder'),
  'LIB_COU_BUCKET':(
      extractStringNormalize, lambda x, y: checkAgainstVocabulary(checkCOUBucket(x, y), 'cou_buckets'), 'cou_bucket'),
  'LIB_PARENT_MODIFIED':(
      extractBoolean, lambda x, y: x, 'is_derived'),
  'LIB_PARENT_TITLE':(
      extractString, lambda x, y: x, 'derived_title'),
  'LIB_PARENT_URL':(
      extractString, checkURL, 'derived_url'),
  'LIB_PARENT_CHANGES':(
      extractString, lambda x, y: x, 'derived_why'),
  'LIB_CKSUM':(
      extractString, lambda x, y: x, 'cksum'),
  'LIB_CURRIC_STANDARDS':(
      extractString, lambda x, y: x, 'curriculum_standards'),
}


try:
    filename = sys.argv[1]
except:
    print 'You should specify the filename'
    raise
    sys.exit(0)

if not filename:
    print 'You should specify the filename'
    sys.exit(0)

try:
    f = open(filename)
except:
    errors['filename'] = 'Can\'t open this file %s' % filename
    sys.exit(0)

reader = csv.reader(f)

errors = []

header = [s.upper() for s in reader.next()]

unknownColumns = []

try:
    if header[0].startswith('CR_'):
        fieldsDefinition = COURSE_FIELDS
        contentType = COURSE_TYPE
        titleFieldName = 'CR_TITLE'
        urlFieldName = 'CR_URL'
    elif header[0].startswith('LIB_'):
        fieldsDefinition = LIBRARY_FIELDS
        contentType = LIBRARY_TYPE
        titleFieldName = 'LIB_TITLE'
        urlFieldName = 'LIB_URL'
    else:
        raise ValueError()

    fieldMap = {}
    for i, v in enumerate(header):
        if v in fieldsDefinition:
            fieldMap[v] = i
        else:
            unknownColumns.append(v)
except:
    raise
    print u'Invalid format of CSV file'
    sys.exit()

if unknownColumns:
    print u'Uknown columns: %s' % u', '.join(unknownColumns)

importedURLs = set()
importedNames = set()

titles = []
urls = []

def normalizeTitle(title):
    return "".join(re.findall("[^%s%s]" % (string.punctuation, string.whitespace), title)).lower()

def normalizeURL(url):
    return urllib.quote(url.strip().strip('/'))


def decode(s):
	try:
		return s.decode("utf-8")
	except UnicodeDecodeError:
		encoding = chardet.detect(s)["encoding"]
		return s.decode(encoding)


for rowIndex, row in enumerate(reader):
    lineNumber = rowIndex + 2
    data = {}

    for extract, validate, attributeName in fieldsDefinition.values():
        data[attributeName] = None

    for fieldName, columnIndex in fieldMap.items():
        if fieldName in unknownColumns:
            continue
        extract, validate, attributeName = fieldsDefinition[fieldName]
        try:
            try:
                rawValue = decode(row[columnIndex])
            except:
                print row[columnIndex]
                raise
        except IndexError:
            errors.append((lineNumber, fieldName, u"Missing column"))
            continue
        try:
            value = extract(rawValue)
        except:
            errors.append((lineNumber, fieldName, u"Can't extract value: %s" % rawValue))
            continue
        data[attributeName] = value
        if attributeName == 'title':
            titles.append((lineNumber, value, normalizeTitle(value)))
        elif attributeName == 'remote_url':
            urls.append((lineNumber, value, normalizeURL(value)))

    for fieldName, (extract, validate, attributeName) in fieldsDefinition.items():
        if fieldName in unknownColumns:
            continue
        value = data[attributeName]
        try:
            validate(value, data)
        except:
            errors.append((lineNumber, fieldName, sys.exc_info()[1]))

titlesDict = {}

for lineNumber, title, normalizedTitle in titles:
    if normalizedTitle not in titlesDict:
        titlesDict[normalizedTitle] = [(lineNumber, title)]
    else:
        titlesDict[normalizedTitle].append((lineNumber, title))

for normalizedTitle, value in titlesDict.items():
    if len(value) > 1:
        for lineNumber, title in value:
            errors.append((lineNumber, titleFieldName, u'Duplicate title: %s' % title))


urlsDict = {}

for lineNumber, url, normalizedURL in urls:
    if normalizedURL not in urlsDict:
        urlsDict[normalizedURL] = [(lineNumber, url)]
    else:
        urlsDict[normalizedURL].append((lineNumber, url))


for normalizedURL, value in urlsDict.items():
    if len(value) > 1:
        for lineNumber, url in value:
            errors.append((lineNumber, urlFieldName, u'Duplicate URL: %s' % url))



if errors:
    out_filename = filename.split('.')[0] + '_errors.csv'
    out_file = open(out_filename, 'w+b')
    writer = csv.writer(out_file)
    writer.writerow(('LINE', 'FIELD', 'ERROR'))
    for row in errors:
        row = [unicode(r).encode('utf-8') for r in row]
        writer.writerow(row)
    out_file.close()

else:
    print "Data is valid"
