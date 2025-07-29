from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from app.tests.utils import (
    AUTH_COOKIE_ACCESS,
    ACCESS_TOKEN_LIFETIME,
    AppTestCase,
)


class APITokenRefreshTestCase(AppTestCase):

    url_name = 'app:api_token_refresh'
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

        # expire
        self.set_at(self.user, expired=True)

        # refresh
        self.set_rt(self.user)
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)

        # check cookie
        at = AccessToken(self.client.cookies[AUTH_COOKIE_ACCESS].value)
        now_timestamp = timezone.now().timestamp()
        self.assertGreater(
            at.payload['exp'],
            now_timestamp + ACCESS_TOKEN_LIFETIME.total_seconds() - 1,
        )
