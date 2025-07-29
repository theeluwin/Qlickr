from uuid import uuid4

from django.urls import reverse
from django.conf import settings
from django.core.cache import cache

from app.tests.utils import AppTestCase


class APIUserPasswordResetTestCase(AppTestCase):

    url_name = 'app:api_user_password_reset'
    allowed_methods = ['PATCH']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=None)

    def test_PATCH_success(self):

        # prepare data
        ticket = str(uuid4())
        email = self.user.username
        cache.set(
            f'password_reset:ticket:{ticket}',
            email,
            timeout=settings.EMAIL_RETRY_DELAY,
        )

        # update data
        new_password = self.generate_data()['password']
        res = self.client.patch(self.url, {
            'ticket': ticket,
            'password': new_password,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertIsNone(cache.get(f'password_reset:ticket:{ticket}'))

    def test_PATCH_fail__empty_ticket(self):
        new_password = self.generate_data()['password']
        res = self.client.patch(self.url, {
            'password': new_password,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__invalid_ticket(self):
        new_password = self.generate_data()['password']
        res = self.client.patch(self.url, {
            'ticket': 'invalid_ticket',
            'password': new_password,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__empty_password(self):

        # prepare data
        ticket = str(uuid4())
        email = self.user.username
        cache.set(
            f'password_reset:ticket:{ticket}',
            email,
            timeout=settings.EMAIL_RETRY_DELAY,
        )

        # update data
        res = self.client.patch(self.url, {
            'ticket': ticket,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__short_password(self):

        # prepare data
        ticket = str(uuid4())
        email = self.user.username
        cache.set(
            f'password_reset:ticket:{ticket}',
            email,
            timeout=settings.EMAIL_RETRY_DELAY,
        )

        # update data
        res = self.client.patch(self.url, {
            'ticket': ticket,
            'password': 'short',
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__common_password(self):

        # prepare data
        ticket = str(uuid4())
        email = self.user.username
        cache.set(
            f'password_reset:ticket:{ticket}',
            email,
            timeout=settings.EMAIL_RETRY_DELAY,
        )

        # update data
        res = self.client.patch(self.url, {
            'ticket': ticket,
            'password': '12345678',
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__similar_password(self):

        # prepare data
        ticket = str(uuid4())
        email = self.user.username
        cache.set(
            f'password_reset:ticket:{ticket}',
            email,
            timeout=settings.EMAIL_RETRY_DELAY,
        )

        # update data
        email = self.user.username
        res = self.client.patch(self.url, {
            'ticket': ticket,
            'password': email.split('@')[0],
        })
        self.assertEqual(res.status_code, 400)
