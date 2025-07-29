from uuid import uuid4

from django.urls import reverse
from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.test.utils import override_settings

from app.tests.utils import AppTestCase


class APIUserPasswordRequestTestCase(AppTestCase):

    url_name = 'app:api_user_password_request'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=None)

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
    )
    def test_POST_success(self):

        # request data
        email = self.user.username
        res = self.client.post(self.url, {
            'email': email,
        })
        self.assertEqual(res.status_code, 201)

        # check data
        self.assertEqual(len(mail.outbox), 1)
        self.assertListEqual(
            mail.outbox[0].to,
            [email],
        )
        self.assertEqual(
            mail.outbox[0].from_email,
            settings.EMAIL_HOST_USER,
        )
        email_key = f'password_reset:email:{email}'
        ticket = cache.get(email_key)
        ticket_key = f'password_reset:ticket:{ticket}'
        cached_email = cache.get(ticket_key)
        self.assertEqual(cached_email, email)
        self.assertGreater(
            cache.ttl(email_key),
            settings.EMAIL_RETRY_DELAY - 1,
        )
        self.assertGreater(
            cache.ttl(ticket_key),
            settings.EMAIL_RETRY_DELAY - 1,
        )

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
    )
    def test_POST_success__wrong_email(self):

        # request data
        email = 'wrong.email@test.ac.kr'
        res = self.client.post(self.url, {
            'email': email,
        })
        self.assertEqual(res.status_code, 201)

        # check data
        self.assertEqual(len(mail.outbox), 0)
        email_key = f'password_reset:email:{email}'
        self.assertGreater(
            cache.ttl(email_key),
            settings.EMAIL_RETRY_DELAY - 1,
        )

    def test_POST_fail__empty_email(self):
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__invalid_email(self):
        res = self.client.post(self.url, {
            'email': 'invalid_email',
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__recent_email(self):

        # prepare data
        ticket = str(uuid4())
        email = self.user.username
        cache.set(
            f'password_reset:email:{email}',
            ticket,
            timeout=settings.EMAIL_RETRY_DELAY,
        )

        # request data
        email = self.user.username
        res = self.client.post(self.url, {
            'email': email,
        })
        self.assertEqual(res.status_code, 400)
