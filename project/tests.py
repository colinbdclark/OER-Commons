from django.core.urlresolvers import reverse
from django.test.testcases import TestCase


class FrontpageTestCase(TestCase):
    
    def test_frontpage(self):
        url = reverse("frontpage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        