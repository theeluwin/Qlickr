from django.urls import reverse

from app.models import (
    Lesson,
    Quiz,
)
from app.tests.utils import AppTestCase


class APIInstructorDashboardTestCase(AppTestCase):

    url_name = 'app:api_instructor_dashboard'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]
        self.quiz = self.quizzes[(1, 1)]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_normal_fail(self):
        self.common_api_normal_fail('GET')

    def test_GET_success__inactive_lesson(self):

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.assertIsNone(res.data['quiz'])
        self.assertEqual(len(res.data['data']), 0)

    def test_GET_success__active_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.assertIsNone(res.data['quiz'])
        self.assertEqual(len(res.data['data']), 0)

    def test_GET_success__active_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.assertEqual(
            res.data['quiz']['id'],
            self.quiz.id,
        )
        self.assertEqual(
            len(res.data['data']),
            len(self.normal_users),
        )
        for row in res.data['data']:
            self.assertEqual(
                row['response']['quiz_id'],
                self.quiz.id,
            )

    def test_GET_success__reviewing_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_REVIEWING
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.assertEqual(
            res.data['quiz']['id'],
            self.quiz.id,
        )
        self.assertEqual(
            len(res.data['data']),
            len(self.normal_users),
        )
        for row in res.data['data']:
            self.assertEqual(
                row['response']['quiz_id'],
                self.quiz.id,
            )
