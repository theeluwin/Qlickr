from django.urls import reverse

from app.tests.utils import (
    AUTH_COOKIE_ACCESS,
    AUTH_COOKIE_REFRESH,
    AppTestCase,
)


class APITokenLogoutTestCase(AppTestCase):

    url_name = 'app:api_token_logout'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__refresh(user=self.user)

    def test_POST_success(self):

        # logout
        self.set_rt(self.user)
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)

        # check cookie
        self.assertEqual(self.client.cookies[AUTH_COOKIE_ACCESS].value, '')
        self.assertEqual(self.client.cookies[AUTH_COOKIE_REFRESH].value, '')
