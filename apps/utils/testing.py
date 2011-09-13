from django.test.testcases import TestCase as BaseTestCase
from django.utils.encoding import smart_str
import re


WHITESPACE_RE = re.compile(r"\s")


class TestCase(BaseTestCase):

    def assertContainsIgnoreWhitespace(self, response, text, count=None, status_code=200,
                       msg_prefix=''):
        """
        Asserts that a response indicates that some content was retrieved
        successfully, (i.e., the HTTP status code was as expected), and that
        ``text`` occurs ``count`` times in the content of the response.
        If ``count`` is None, the count doesn't matter - the assertion is true
        if the text occurs at least once in the response.
        """
        if msg_prefix:
            msg_prefix += ": "

        self.assertEqual(response.status_code, status_code,
            msg_prefix + "Couldn't retrieve content: Response code was %d"
            " (expected %d)" % (response.status_code, status_code))
        text = smart_str(text, response._charset)
        real_count = WHITESPACE_RE.sub("", response.content).count(WHITESPACE_RE.sub("", text))
        if count is not None:
            self.assertEqual(real_count, count,
                msg_prefix + "Found %d instances of '%s' in response"
                " (expected %d)" % (real_count, text, count))
        else:
            self.assertTrue(real_count != 0,
                msg_prefix + "Couldn't find '%s' in response" % text)

    def assertNotContainsIgnoreWhitespace(self, response, text, status_code=200,
                          msg_prefix=''):
        """
        Asserts that a response indicates that some content was retrieved
        successfully, (i.e., the HTTP status code was as expected), and that
        ``text`` doesn't occurs in the content of the response.
        """
        if msg_prefix:
            msg_prefix += ": "

        self.assertEqual(response.status_code, status_code,
            msg_prefix + "Couldn't retrieve content: Response code was %d"
            " (expected %d)" % (response.status_code, status_code))
        text = smart_str(text, response._charset)
        self.assertEqual(WHITESPACE_RE.sub("", response.content).count(WHITESPACE_RE.sub("", text)), 0,
            msg_prefix + "Response should not contain '%s'" % text)
