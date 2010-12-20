import elementtree.ElementTree as etree
import socket
import time
import urllib2


MAX_RETRY = 10


class CcRest:
    """Wrapper class to decompose REST XML responses into Python objects."""

    def __init__(self, root, lang='en'):
        self.root = root

        self.__lc_doc = None

        self.set_default_lang(lang)

    def set_default_lang(self, lang):
        """Set the default language for web service requests."""

        # retrieve the list of supported locales
        locale_url = '%s/locales' % self.root
        locale_doc = etree.fromstring(urllib2.urlopen(locale_url).read())

        # extract the list of support locales
        supported_locales = [n.attrib['id'] for n in
                             locale_doc.findall('locale')]

        if lang not in supported_locales:
            if lang.split('_')[0] in supported_locales:
                # try the generic version of the language ("un-nationalized")
                lang = lang.split('_')[0]

            else:
                # fall back to English
                lang = 'en'

        self.__default_lang = lang

    def license_classes(self, lang=None):
        """Returns a dictionary whose keys are license IDs, with the
        license label as the value."""

        # use the default language if none is specified
        if lang is None:
            lang = self.__default_lang

        lc_url = '%s/classes?locale=%s' % (self.root, lang)

        # retrieve the licenses document and store it
        self.__lc_doc = urllib2.urlopen(lc_url).read()

        # parse the document and return a dictionary
        lc = {}
        d = etree.fromstring(self.__lc_doc)

        licenses = d.findall('license')

        for l in licenses:
            lc[l.attrib['id']] = l.text

        return lc

    def fields(self, license, lang=None):
        """Retrieves details for a particular license."""

        # use the default language if none is specified
        if lang is None:
            lang = self.__default_lang

        l_url = '%s/license/%s?locale=%s' % (self.root, license, lang)

        # retrieve the license source document
        self.__l_doc = urllib2.urlopen(l_url).read()

        d = etree.fromstring(self.__l_doc)

        self._cur_license = {}
        keys = []

        fields = d.findall('field')

        for field in fields:
            f_id = field.attrib['id']
            keys.append(f_id)

            self._cur_license[f_id] = {}

            self._cur_license[f_id]['label'] = field.find('label').text
            self._cur_license[f_id]['description'] = \
                              field.find('description').text
            self._cur_license[f_id]['type'] = field.find('type').text
            self._cur_license[f_id]['enum'] = {}

            # extract the enumerations
            enums = field.findall('enum')
            for e in enums:
                e_id = e.attrib['id']
                self._cur_license[f_id]['enum'][e_id] = \
                     e.find('label').text

        self._cur_license['__keys__'] = keys
        return self._cur_license

    def __answers_xml(self, license, answers, workinfo, lang):
        """Construct answers.xml."""

        # construct the answers.xml document from the answers dictionary
        answer_xml = u"""
        <answers>
          <locale>%s</locale>
          <license-%s>""" % (lang, license)

        for key in answers:
            answer_xml = u"""%s
            <%s>%s</%s>""" % (answer_xml, key, answers[key], key)

        answer_xml = u"""%s
          </license-%s>
          <work-info>
        """ % (answer_xml, license)

        for key in workinfo:
            answer_xml = u"""%s
            <%s>%s</%s>""" % (answer_xml, key, workinfo[key], key)

        answer_xml = u"""%s
          </work-info>
        </answers>
        """ % (answer_xml)

        return answer_xml

    def issue(self, license, answers, workinfo={}, lang=None):

        retry_count = 0

        # use the default language if none is specified
        if lang is None:
            lang = self.__default_lang

        l_url = '%s/license/%s/issue' % (self.root, license)
        answer_xml = self.__answers_xml(license, answers, workinfo, lang)

        while (retry_count < MAX_RETRY):
            # retrieve the license source document
            try:
                # retrieve the license information from the web service
                self.__a_doc = urllib2.urlopen(l_url,
                                       data=u'answers=%s' % answer_xml).read()

                return self.__a_doc
            except (socket.error, urllib2.HTTPError), e:
                # check if this is our last attempt
                if retry_count == MAX_RETRY - 1:
                    # re-raise the exception
                    raise e
                else:
                    retry_count = retry_count + 1

                # sleep so we don't hammer the server
                time.sleep(1)


