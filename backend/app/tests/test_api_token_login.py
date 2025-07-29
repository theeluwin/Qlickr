from django.urls import reverse

from app.tests.utils import AppTestCase


class APITokenLoginTestCase(AppTestCase):

    url_name = 'app:api_token_login'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user_data = self.normal_datas[1]['user']

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=None)

    def test_POST_success(self):
        res = self.client.post(self.url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        })
        self.assertEqual(res.status_code, 200)

    def test_POST_fail__empty_data(self):
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__empty_username(self):
        res = self.client.post(self.url, {
            'password': self.user_data['password'],
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__wrong_username(self):
        res = self.client.post(self.url, {
            'username': 'wrong_username',
            'password': self.user_data['password'],
        })
        self.assertEqual(res.status_code, 401)

    def test_POST_fail__empty_password(self):
        res = self.client.post(self.url, {
            'username': self.user_data['username'],
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__wrong_password(self):
        res = self.client.post(self.url, {
            'username': self.user_data['username'],
            'password': 'wrong_password',
        })
        self.assertEqual(res.status_code, 401)
