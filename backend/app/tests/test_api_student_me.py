from django.db import connection
from django.urls import reverse
from django.test.utils import CaptureQueriesContext

from app.tests.utils import AppTestCase


class APIStudentMeTestCase(AppTestCase):

    url_name = 'app:api_student_me'
    allowed_methods = ['GET', 'PATCH']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]
        self.student = self.students[1]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_admin_fail(self):
        self.set_at(self.admin_user)
        for method in self.allowed_methods:
            method = method.lower()
            requester = getattr(self.client, method)
            res = requester(self.url)
            self.assertEqual(res.status_code, 404)

    def test_GET_success(self):

        # get data (special: user should join student)
        self.set_at(self.user)
        with CaptureQueriesContext(connection) as ctx:
            res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(ctx.captured_queries), 2)  # get student (fetched from user), get quiz count

        # check data
        self.assertEqual(
            res.data['personal_sid'],
            self.student.personal_sid,
        )

    def test_PATCH_success__empty(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {})
        self.assertEqual(res.status_code, 200)

    def test_PATCH_success__personal_sid(self):

        # update data
        self.set_at(self.user)
        new_personal_sid = self.generate_data()['personal_sid']
        res = self.client.patch(self.url, {
            'personal_sid': new_personal_sid,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.student.refresh_from_db()
        self.assertEqual(
            self.student.personal_sid,
            new_personal_sid,
        )

    def test_PATCH_success__personal_name(self):

        # update data
        self.set_at(self.user)
        new_personal_name = self.generate_data()['personal_name']
        res = self.client.patch(self.url, {
            'personal_name': new_personal_name,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.student.refresh_from_db()
        self.assertEqual(
            self.student.personal_name,
            new_personal_name,
        )

    def test_PATCH_success__role_department(self):

        # update data
        self.set_at(self.user)
        new_role_department = self.generate_data()['role_department']
        res = self.client.patch(self.url, {
            'role_department': new_role_department,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.student.refresh_from_db()
        self.assertEqual(
            self.student.role_department,
            new_role_department,
        )

    def test_PATCH_success__role_major(self):

        # update data
        self.set_at(self.user)
        new_role_major = self.generate_data()['role_major']
        res = self.client.patch(self.url, {
            'role_major': new_role_major,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.student.refresh_from_db()
        self.assertEqual(self.student.role_major, new_role_major)

    def test_PATCH_success__role_year(self):

        # update data
        self.set_at(self.user)
        new_role_year = self.generate_data()['role_year']
        res = self.client.patch(self.url, {
            'role_year': new_role_year,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        self.student.refresh_from_db()
        self.assertEqual(self.student.role_year, new_role_year)

    def test_PATCH_fail__personal_sid_too_long(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'personal_sid': '_' * 21,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__personal_name_too_long(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'personal_name': '_' * 41,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__role_department_too_long(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'role_department': '_' * 41,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__role_major_too_long(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'role_major': '_' * 41,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__role_year_underflow(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'role_year': -1,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__role_year_overflow(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'role_year': 2 ** 15,
        })
        self.assertEqual(res.status_code, 400)

    def test_PATCH_fail__role_year_wrong_type(self):
        self.set_at(self.user)
        res = self.client.patch(self.url, {
            'role_year': 'new_role_year',
        })
        self.assertEqual(res.status_code, 400)
