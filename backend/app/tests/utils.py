import random

from uuid import uuid4
from datetime import timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import (
    override_settings,
    TransactionTestCase,
)
from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
)
from rest_framework.test import APIClient
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator

from project.asgi import application
from app.models import (
    Student,
    Lesson,
    Quiz,
    Option,
    Response,
)


HTTP_METHODS = [
    'GET',
    'PUT',
    'DELETE',
    'POST',
    'PATCH',
]
AUTH_COOKIE_ACCESS = settings.SIMPLE_JWT['AUTH_COOKIE_ACCESS']
AUTH_COOKIE_REFRESH = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']
ACCESS_TOKEN_LIFETIME = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
REFRESH_TOKEN_LIFETIME = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
WS_CONNECT_TIMEOUT = 1

User = get_user_model()


@override_settings(
    PASSWORD_HASHERS=[
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ],
    TEST_DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    },
)
class AppTestCase(TransactionTestCase):

    def init_data(self):

        # reset cache
        cache.clear()

        # init manager
        self.admin_data = {
            'user': {
                'username': 'admin',
                'password': 'test_admin_password'
            },
        }
        self.admin_user = User.objects.create_user(
            username=self.admin_data['user']['username'],
            password=self.admin_data['user']['password'],
            is_staff=True,
        )

        # init students
        self.normal_datas = {}
        self.normal_users = {}
        self.students = {}
        for n in range(1, 2 + 1):
            self.normal_datas[n] = {
                'user': {
                    'username': f'student{n}@test.ac.kr',
                    'password': f'test_student{n}_password'
                },
                'profile': {
                    'personal_sid': f'2025-0000{n}',
                }
            }
            self.normal_users[n] = User.objects.create_user(
                username=self.normal_datas[n]['user']['username'],
                password=self.normal_datas[n]['user']['password'],
            )
            self.students[n], _ = Student.objects.update_or_create(
                user=self.normal_users[n],
                defaults=self.normal_datas[n]['profile']
            )

        # init lessons
        self.lessons = {}
        for i in range(1, 3 + 1):
            self.lessons[i], _ = Lesson.objects.get_or_create(
                seq=i,
                defaults={
                    'date': '2025-01-01',
                },
            )

        # init quizzes
        self.quizzes = {}
        for i in range(1, 3 + 1):
            for j in range(1, 3 + 1):
                self.quizzes[(i, j)], _ = Quiz.objects.get_or_create(
                    lesson=self.lessons[i],
                    order=j,
                    defaults={
                        'answer': j,
                        'content': f"Test Quiz {i}-{j}",
                    },
                )

        # init options
        self.options = {}
        for i in range(1, 3 + 1):
            for j in range(1, 2 + 1):
                for k in range(1, 2 + 1):
                    self.options[(i, j, k)], _ = Option.objects.get_or_create(
                        quiz=self.quizzes[(i, j)],
                        order=k,
                        defaults={
                            'content': f"Test Option {i}-{j}-{k}",
                        },
                    )

        # init ress
        self.responses = {}
        for n in range(1, 2 + 1):
            for i in range(1, 3 + 1):
                for j in range(1, 2 + 1):
                    self.responses[(i, j, n)], _ = Response.objects.get_or_create(
                        user=self.normal_users[n],
                        quiz=self.quizzes[(i, j)],
                        defaults={
                            'option_id': self.options[(i, j, n)].id,
                        },
                    )

    def generate_data(self):
        pin = random.randint(1000, 9999)
        return {
            'username': f'test{pin}@test.ac.kr',
            'password': str(uuid4()),
            'personal_sid': f'2025-{pin}',
            'personal_name': f'Student {pin}',
            'role_department': f'Department {pin}',
            'role_major': f'Major {pin}',
            'role_year': random.randint(1, 4),
        }

    def set_at(self, user, expired=False):
        at = AccessToken.for_user(user)
        if expired:
            expired_time = timezone.now() - ACCESS_TOKEN_LIFETIME - timedelta(seconds=1)
            at.set_exp(from_time=expired_time)
        self.client.cookies[AUTH_COOKIE_ACCESS] = str(at)
        self.aclient.cookies[AUTH_COOKIE_ACCESS] = str(at)

    def set_rt(self, user, expired=False):
        rt = RefreshToken.for_user(user)
        if expired:
            expired_time = timezone.now() - REFRESH_TOKEN_LIFETIME - timedelta(seconds=1)
            rt.set_exp(from_time=expired_time)
        self.client.cookies[AUTH_COOKIE_REFRESH] = str(rt)
        self.aclient.cookies[AUTH_COOKIE_REFRESH] = str(rt)

    async def get_wsc(self, user):
        self.set_at(user)
        res = await self.aclient.post(
            reverse('app:api_websocket_ticket'),
            {},
        )
        ticket = res.data['ticket']
        wsc = WebsocketCommunicator(
            application,
            f'{self.url}?ticket={ticket}',
        )
        connected, close_code = await wsc.connect(timeout=WS_CONNECT_TIMEOUT)
        return wsc, (connected, close_code)

    def common_api_method_fail(self, user=None):
        if user:
            self.set_at(user)
        for method in HTTP_METHODS:
            if method in self.allowed_methods:
                continue
            res = getattr(self.client, method.lower())(self.url, {})
            self.assertEqual(res.status_code, 405)

    def common_api_auth_fail__access(self, user):
        for method in self.allowed_methods:
            requester = getattr(self.client, method.lower())

            # empty token
            res = requester(self.url, {})
            self.assertEqual(res.status_code, 401)

            # invalid token
            self.client.cookies[AUTH_COOKIE_ACCESS] = 'invalid_token'
            res = requester(self.url, {})
            self.assertEqual(res.status_code, 401)

            # expired token
            self.set_at(user, expired=True)
            res = requester(self.url, {})
            self.assertEqual(res.status_code, 401)

    def common_api_auth_fail__refresh(self, user):
        for method in self.allowed_methods:
            requester = getattr(self.client, method.lower())

            # empty token
            res = requester(self.url, {})
            self.assertEqual(res.status_code, 400)

            # invalid token
            self.client.cookies[AUTH_COOKIE_REFRESH] = 'invalid_token'
            res = requester(self.url, {})
            self.assertEqual(res.status_code, 401)

            # expired token
            self.set_rt(user, expired=True)
            res = requester(self.url, {})
            self.assertEqual(res.status_code, 401)

    def common_api_normal_fail(self, method):
        requester = getattr(self.client, method.lower())
        for n in range(1, 2 + 1):
            self.set_at(self.normal_users[n])
            res = requester(self.url, {})
            self.assertEqual(res.status_code, 403)

    def common_api_detail_fail(self, user=None):
        if user:
            self.set_at(user)
        for method in self.allowed_methods:
            requester = getattr(self.client, method.lower())
            url = reverse(self.url_name, args=[
                0,
            ])
            res = requester(url, {})
            self.assertEqual(res.status_code, 404)

    async def common_ws_auth_fail(self):

        # empty ticket
        wsc = WebsocketCommunicator(application, self.url)
        connected, close_code = await wsc.connect(
            timeout=WS_CONNECT_TIMEOUT,
        )
        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)

        # invalid ticket (expired ticket will be deleted)
        wsc = WebsocketCommunicator(
            application,
            f'{self.url}?ticket=invalid_ticket',
        )
        connected, close_code = await wsc.connect(
            timeout=WS_CONNECT_TIMEOUT,
        )
        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)

    async def common_ws_normal_fail(self):
        for n in range(1, 2 + 1):
            _, (connected, close_code) = await self.get_wsc(self.normal_users[n])
            self.assertEqual(connected, False)
            self.assertEqual(close_code, 4003)

    def setUp(self):
        self.client = APIClient()
        self.aclient = APIClient()
        self.aclient.get = sync_to_async(self.aclient.get)
        self.aclient.put = sync_to_async(self.aclient.put)
        self.aclient.delete = sync_to_async(self.aclient.delete)
        self.aclient.post = sync_to_async(self.aclient.post)
        self.aclient.patch = sync_to_async(self.aclient.patch)
        self.init_data()
