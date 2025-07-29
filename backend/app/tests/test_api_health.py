from django.urls import reverse

from app.tests.utils import AppTestCase


class APIHealthTestCase(AppTestCase):

    url_name = 'app:api_health'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=None)

    def test_GET_success(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
