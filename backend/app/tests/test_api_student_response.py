from django.urls import reverse

from app.models import (
    Lesson,
    Quiz,
    Response,
)
from app.tests.utils import AppTestCase


class APIStudentResponseListTestCase(AppTestCase):

    url_name = 'app:api_student_response-list'
    allowed_methods = ['GET', 'POST']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]
        self.lesson = self.lessons[1]
        self.quiz = self.quizzes[(1, 1)]
        self.option = self.options[(1, 1, 1)]
        self.option_other = self.options[(1, 1, 2)]
        self.option_foreign = self.options[(1, 2, 1)]
        self.response = self.responses[(1, 1, 1)]

        # basic url
        self.url = reverse(self.url_name)

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_GET_success(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url, params={
            'quiz': self.quiz.id,
        })
        self.assertEqual(res.status_code, 200)

        # check data
        response = Response.objects.get(
            user=self.user,
            quiz=self.quiz,
        )
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(len(res.data['results']), 1)
        response_data = res.data['results'][0]
        self.assertEqual(
            response_data['username'],
            response.user.username,
        )
        self.assertEqual(
            response_data['quiz_id'],
            response.quiz.id,
        )
        self.assertEqual(
            response_data['option_id'],
            response.option.id,
        )

    def test_POST_create_success(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()
        self.response.delete()

        # create data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option.id,
        })
        self.assertEqual(res.status_code, 201)

        # check data
        self.assertEqual(Response.objects.filter(
            user=self.user,
            quiz=self.quiz,
        ).count(), 1)
        self.assertEqual(Response.objects.get(
            user=self.user,
            quiz=self.quiz,
        ).option.id, self.option.id)

    def test_POST_create_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()
        self.response.delete()

        # create data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_create_fail__invalid_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()
        self.response.delete()

        # create data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': 0,
            'option': self.option.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_create_fail__reviewing_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_REVIEWING
        self.quiz.save()
        self.response.delete()

        # create data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_create_fail__closed_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_CLOSED
        self.quiz.save()
        self.response.delete()

        # create data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_create_fail__invalid_option(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()
        self.response.delete()

        # create data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': 0,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_create_fail__wrong_option(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()
        self.response.delete()

        # create data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option_foreign.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_update_success(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # update data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option_other.id,
        })
        self.assertEqual(res.status_code, 201)

        # check data
        self.assertEqual(Response.objects.filter(
            user=self.user,
            quiz=self.quiz,
        ).count(), 1)
        self.assertEqual(Response.objects.get(
            user=self.user,
            quiz=self.quiz,
        ).option.id, self.option_other.id)

    def test_POST_update_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # update data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option_other.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_update_fail__invalid_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # update date
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': 0,
            'option': self.option_other.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_update_fail__reviewing_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_REVIEWING
        self.quiz.save()

        # update data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option_other.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_update_fail__closed_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_CLOSED
        self.quiz.save()

        # update data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option_other.id,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_update_fail__invalid_option(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # update data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': 0,
        })
        self.assertEqual(res.status_code, 400)

    def test_POST_update_fail__wrong_option(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # update data
        self.set_at(self.user)
        res = self.client.post(self.url, data={
            'quiz': self.quiz.id,
            'option': self.option_foreign.id,
        })
        self.assertEqual(res.status_code, 400)


class APIStudentResponseDetailTestCase(AppTestCase):

    url_name = 'app:api_student_response-detail'
    allowed_methods = ['GET']

    def setUp(self):
        super().setUp()

        # data alias
        self.user = self.normal_users[1]
        self.lesson = self.lessons[1]
        self.quiz = self.quizzes[(1, 1)]
        self.option = self.options[(1, 1, 1)]
        self.response = self.responses[(1, 1, 1)]
        self.response_foreign = self.responses[(1, 1, 2)]

        # basic url
        self.url = reverse(self.url_name, args=[
            self.response.id,
        ])

    def test_method_fail(self):
        self.common_api_method_fail(user=self.user)

    def test_auth_fail(self):
        self.common_api_auth_fail__access(user=self.user)

    def test_detail_fail(self):
        self.common_api_detail_fail(user=self.user)

    def test_GET_success(self):

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
            res.data['username'],
            self.user.username,
        )
        self.assertEqual(
            res.data['quiz_id'],
            self.quiz.id,
        )
        self.assertEqual(
            res.data['option_id'],
            self.option.id,
        )

    def test_GET_fail__closed_lesson(self):

        # prepare data
        self.lesson.state = Lesson.STATE_CLOSED
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_GET_fail__reviewing_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_REVIEWING
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_GET_fail__closed_quiz(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_CLOSED
        self.quiz.save()

        # get data
        self.set_at(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_GET_fail__foreign_response(self):

        # prepare data
        self.lesson.state = Lesson.STATE_ACTIVE
        self.lesson.save()
        self.quiz.state = Quiz.STATE_ACTIVE
        self.quiz.save()

        # get data
        url = reverse(self.url_name, args=[
            self.response_foreign.id,
        ])
        self.set_at(self.user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)
