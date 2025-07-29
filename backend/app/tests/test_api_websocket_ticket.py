from django.urls import reverse
from django.core.cache import cache

from app.tests.utils import AppTestCase


class APIWebsocketTicketTestCase(AppTestCase):

    url_name = 'app:api_websocket_ticket'
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
        self.common_api_auth_fail__access(user=self.user)

    def test_POST_success(self):

        # request ticket
        self.set_at(self.user)
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 201)

        # check ticket
        ticket = res.data['ticket']
        key = f'websocket:ticket:{ticket}'
        self.assertEqual(cache.get(key), self.user.id)
