from django.urls import reverse

from app.models import (
    Lesson,
    Quiz,
)
from app.tests.utils import AppTestCase


class APIInstructorQuizListTestCase(AppTestCase):

    url_name = 'app:api_instructor_quiz-list'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_normal_fail(self):
        self.common_api_normal_fail('GET')

    def test_GET_success(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        quiz_datas = res.data['results']
        for i in range(len(quiz_datas) - 1):
            self.assertLess(
                quiz_datas[i]['order'],
                quiz_datas[i + 1]['order'],
            )
        for quiz_data in quiz_datas:
            self.assertEqual(
                quiz_data['lesson_id'],
                self.lesson.seq,
            )

    def test_GET_success__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.assertEqual(res.data['count'], 0)
        self.assertEqual(len(res.data['results']), 0)


class APIInstructorQuizDetailTestCase(AppTestCase):

    url_name = 'app:api_instructor_quiz-detail'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]
        self.quiz = self.quizzes[(1, 1)]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.quiz.id,
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

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.assertEqual(res.data['id'], self.quiz.id)

    def test_GET_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)


class APIInstructorQuizActivateTestCase(AppTestCase):

    url_name = 'app:api_instructor_quiz-activate'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]
        self.quiz_prev = self.quizzes[(1, 1)]
        self.quiz = self.quizzes[(1, 2)]
        self.quiz_next = self.quizzes[(1, 3)]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.quiz.id,
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
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.quiz_prev.refresh_from_db()
        self.quiz.refresh_from_db()
        self.quiz_next.refresh_from_db()
        self.assertEqual(self.quiz_prev.state, Quiz.STATE_CLOSED)
        self.assertEqual(self.quiz.state, Quiz.STATE_ACTIVE)
        self.assertEqual(self.quiz_next.state, Quiz.STATE_PENDING)

    def test_POST_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 404)


class APIInstructorQuizReviewTestCase(AppTestCase):

    url_name = 'app:api_instructor_quiz-review'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]
        self.quiz_prev = self.quizzes[(1, 1)]
        self.quiz = self.quizzes[(1, 2)]
        self.quiz_next = self.quizzes[(1, 3)]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.quiz.id,
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
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.quiz_prev.refresh_from_db()
        self.quiz.refresh_from_db()
        self.quiz_next.refresh_from_db()
        self.assertEqual(self.quiz_prev.state, Quiz.STATE_CLOSED)
        self.assertEqual(self.quiz.state, Quiz.STATE_REVIEWING)
        self.assertEqual(self.quiz_next.state, Quiz.STATE_PENDING)

    def test_POST_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 404)


class APIInstructorQuizCloseTestCase(AppTestCase):

    url_name = 'app:api_instructor_quiz-close'
    allowed_methods = ['POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]
        self.quiz_prev = self.quizzes[(1, 1)]
        self.quiz = self.quizzes[(1, 2)]
        self.quiz_next = self.quizzes[(1, 3)]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.quiz.id,
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
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)

        # check data
        self.quiz_prev.refresh_from_db()
        self.quiz.refresh_from_db()
        self.quiz_next.refresh_from_db()
        self.assertEqual(self.quiz_prev.state, Quiz.STATE_CLOSED)
        self.assertEqual(self.quiz.state, Quiz.STATE_CLOSED)
        self.assertEqual(self.quiz_next.state, Quiz.STATE_PENDING)

    def test_POST_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()

        # request data
        self.set_at(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 404)


class APIInstructorQuizResultsTestCase(AppTestCase):

    url_name = 'app:api_instructor_quiz-results'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.admin_user
        self.lesson = self.lessons[1]
        self.quiz = self.quizzes[(1, 1)]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.quiz.id,
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
        response_count = 0
        for i, j, _ in self.responses:
            if i == self.lesson.seq and j == self.quiz.order:
                response_count += 1
        self.assertEqual(res.data['total'], response_count)

    def test_GET_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_GET_fail__quiz_state_pending(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_PENDING
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 400)

    def test_GET_fail__quiz_state_active(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 400)

    def test_GET_fail__quiz_state_closed(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_CLOSED
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 400)
