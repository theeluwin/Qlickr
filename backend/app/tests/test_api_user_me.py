from django.db import connection
from django.urls import reverse
from django.test.utils import CaptureQueriesContext

from app.tests.utils import AppTestCase


class APIUserMeTestCase(AppTestCase):

    url_name = 'app:api_user_me'
    allowed_methods = ['GET', 'PATCH']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]
        self.user_other = self.normal_users[2]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_GET_success(self):

        # get data (special: user should join student)
        self.set_at(self.user)
        with CaptureQueriesContext(connection) as ctx:
            res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(ctx.captured_queries), 1)

        # check data
        self.assertEqual(res.data['username'], self.user.username)
        self.assertNotIn('password', res.data)
        self.assertEqual(res.data['is_staff'], False)

    def test_PATCH_success__username(self):

        # update data
        self.set_at(self.user)
        new_username = self.generate_data()['username']
        res = self.client.patch(self.url, {
            'username': new_username,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, new_username)

    def test_PATCH_success__password(self):

        # update data
        self.set_at(self.user)
        new_password = self.generate_data()['password']
        res = self.client.patch(self.url, {
            'password': new_password,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_PATCH_fail__empty_data(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {})
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__invalid_username(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'username': 'invalid_username',
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__duplicate_username(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'username': self.user_other.username,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__short_password(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'password': 'short',
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__common_password(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'password': '12345678',
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__similar_password(self):
        self.set_at(self.user)
        email = self.user.username
        res = self.client.patch(self.url, {
            'password': email.split('@')[0],
        })
        self.assertEqual(res.status_code, 400)
