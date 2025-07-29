from django.urls import reverse

from app.models import (
    Lesson,
    Quiz,
)
from app.tests.utils import AppTestCase


class APIInstructorLessonListTestCase(AppTestCase):

    url_name = 'app:api_instructor_lesson-list'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_normal_fail(self):
        self.common_api_normal_fail('GET')

    def test_GET_success(self):

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        lesson_datas = res.data['results']
        self.assertEqual(len(lesson_datas), len(self.lessons))
        for i in range(len(lesson_datas) - 1):
            self.assertLess(
                lesson_datas[i]['seq'],
                lesson_datas[i + 1]['seq'],
            )


class APIInstructorLessonDetailTestCase(AppTestCase):

    url_name = 'app:api_instructor_lesson-detail'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.lesson.seq,
        ])

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_normal_fail(self):
        self.common_api_normal_fail('GET')

    def test_detail_fail(self):
        self.common_api_detail_fail(user=self.user)

    def test_GET_success(self):

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.assertEqual(res.data['seq'], self.lesson.seq)


class APIInstructorLessonActivateTestCase(AppTestCase):

    url_name = 'app:api_instructor_lesson-activate'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson_prev = self.lessons[1]
        self.lesson = self.lessons[2]
        self.lesson_next = self.lessons[3]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.lesson.seq,
        ])

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_normal_fail(self):
        self.common_api_normal_fail('POST')

    def test_detail_fail(self):
        self.common_api_detail_fail(user=self.user)

    def test_POST_success(self):

        # prepare data
        self.lesson_prev.quizzes.update(state=Quiz.STATE_CLOSED)
        self.lesson.quizzes.update(state=Quiz.STATE_ACTIVE)
        self.lesson_next.quizzes.update(state=Quiz.STATE_REVIEWING)

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.lesson_prev.refresh_from_db()
        self.lesson.refresh_from_db()
        self.lesson_next.refresh_from_db()
        self.assertEqual(self.lesson_prev.state, Lesson.STATE_CLOSED)
        self.assertEqual(self.lesson.state, Lesson.STATE_ACTIVE)
        self.assertEqual(self.lesson_next.state, Lesson.STATE_PENDING)
        self.assertEqual(Quiz.objects.filter(
            state__in=[
                Quiz.STATE_ACTIVE,
                Quiz.STATE_REVIEWING,
            ],
        ).count(), 0)


class APIInstructorLessonCloseTestCase(AppTestCase):

    url_name = 'app:api_instructor_lesson-close'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson_prev = self.lessons[1]
        self.lesson = self.lessons[2]
        self.lesson_next = self.lessons[3]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.lesson.seq,
        ])

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_normal_fail(self):
        self.common_api_normal_fail('POST')

    def test_detail_fail(self):
        self.common_api_detail_fail(user=self.user)

    def test_POST_success(self):

        # prepare data
        self.lesson_prev.quizzes.update(state=Quiz.STATE_CLOSED)
        self.lesson.quizzes.update(state=Quiz.STATE_ACTIVE)
        self.lesson_next.quizzes.update(state=Quiz.STATE_REVIEWING)

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.lesson_prev.refresh_from_db()
        self.lesson.refresh_from_db()
        self.lesson_next.refresh_from_db()
        self.assertEqual(self.lesson_prev.state, Lesson.STATE_CLOSED)
        self.assertEqual(self.lesson.state, Lesson.STATE_CLOSED)
        self.assertEqual(self.lesson_next.state, Lesson.STATE_PENDING)
        self.assertEqual(Quiz.objects.filter(
            state__in=[
                Quiz.STATE_ACTIVE,
                Quiz.STATE_REVIEWING,
            ],
        ).count(), 0)
