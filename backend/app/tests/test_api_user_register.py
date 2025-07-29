from django.urls import reverse
from django.contrib.auth import get_user_model

from app.tests.utils import AppTestCase


User = get_user_model()


class APIUserRegisterTestCase(AppTestCase):

    url_name = 'app:api_user_register'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]
        self.student = self.students[1]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=None)

    def test_POST_success(self):

        # create data
        data = self.generate_data()
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 201)

        # check data
        self.assertTrue(User.objects.filter(
            username=data['username'],
        ).exists())
        user = User.objects.get(
            username=data['username'],
        )
        self.assertEqual(user.is_staff, False)
        self.assertEqual(
            user.student.personal_sid,
            data['personal_sid'],
        )

    def test_POST_fail__empty_username(self):
        data = self.generate_data()
        del data['username']
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__invalid_username(self):
        data = self.generate_data()
        data['username'] = 'invalid_username'
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__existing_username(self):
        data = self.generate_data()
        data['username'] = self.user.username
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__empty_password(self):
        data = self.generate_data()
        del data['password']
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__short_password(self):
        data = self.generate_data()
        data['password'] = 'short'
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__common_password(self):
        data = self.generate_data()
        data['password'] = '12345678'
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__similar_password(self):
        data = self.generate_data()
        email = data['username']
        data['password'] = email.split('@')[0]
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__empty_personal_sid(self):
        data = self.generate_data()
        del data['personal_sid']
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__existing_personal_sid(self):
        data = self.generate_data()
        data['personal_sid'] = self.student.personal_sid
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__personal_sid_too_long(self):
        data = self.generate_data()
        data['personal_sid'] = '_' * 21
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__empty_personal_name(self):
        data = self.generate_data()
        del data['personal_name']
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__personal_name_too_long(self):
        data = self.generate_data()
        data['personal_name'] = '_' * 41
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__role_department_too_long(self):
        data = self.generate_data()
        data['role_department'] = '_' * 41
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__role_major_too_long(self):
        data = self.generate_data()
        data['role_major'] = '_' * 41
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__role_year_underflow(self):
        data = self.generate_data()
        data['role_year'] = -1
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__role_year_overflow(self):
        data = self.generate_data()
        data['role_year'] = 2 ** 15
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)

    def test_POST_fail__role_year_wrong_type(self):
        data = self.generate_data()
        data['role_year'] = 'new_role_year'
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
