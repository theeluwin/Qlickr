from django.urls import reverse

from app.models import Quiz
from app.tests.utils import AppTestCase


class WSInstructorTestCase(AppTestCase):

    url = '/ws/instructor/'

    def setUp(self):
        super().setUp()

        # data alias
        self.admin = self.admin_user
        self.user = self.admin_user
        self.lesson = self.lessons[1]
        self.quiz = self.quizzes[(1, 1)]

    async def test_auth_fail(self):
        await self.common_ws_auth_fail()

    async def test_receive_success__nothing(self):

        # connect
        wsc, _ = await self.get_wsc(self.user)

        # receive data
        data = await wsc.receive_json_from()
        self.assertEqual(
            data['type'],
            'instructor_live_quiz',
        )

        # check data
        quiz_data = data['quiz_data']
        self.assertIsNone(quiz_data)

    async def test_receive_success__activate_lesson(self):

        # connect
        wsc, _ = await self.get_wsc(self.user)
        await wsc.receive_json_from()

        # activate lesson
        self.set_at(self.admin)
        url = reverse('app:api_instructor_lesson-activate', args=[
            self.lesson.seq,
        ])
        await self.aclient.post(url)

        # receive data
        data = await wsc.receive_json_from()
        self.assertEqual(
            data['type'],
            'instructor_live_quiz',
        )

        # check data
        quiz_data = data['quiz_data']
        self.assertIsNone(quiz_data)

    async def test_receive_success__close_lesson(self):

        # connect
        wsc, _ = await self.get_wsc(self.user)
        await wsc.receive_json_from()

        # close lesson
        self.set_at(self.admin)
        url = reverse('app:api_instructor_lesson-close', args=[
            self.lesson.seq,
        ])
        await self.aclient.post(url)

        # receive data
        data = await wsc.receive_json_from()
        self.assertEqual(
            data['type'],
            'instructor_live_quiz',
        )

        # check data
        quiz_data = data['quiz_data']
        self.assertIsNone(quiz_data)

    async def test_receive_success__activate_quiz(self):

        # connect
        wsc, _ = await self.get_wsc(self.user)
        await wsc.receive_json_from()

        # activate lesson
        self.set_at(self.admin)
        url = reverse('app:api_instructor_lesson-activate', args=[
            self.lesson.seq,
        ])
        await self.aclient.post(url)
        await wsc.receive_json_from()

        # activate quiz
        self.set_at(self.admin)
        url = reverse('app:api_instructor_quiz-activate', args=[
            self.quiz.id,
        ])
        await self.aclient.post(url)

        # receive data
        data = await wsc.receive_json_from()
        self.assertEqual(
            data['type'],
            'instructor_live_quiz',
        )

        # check data
        quiz_data = data['quiz_data']
        self.assertEqual(quiz_data['id'], self.quiz.id)
        self.assertEqual(quiz_data['state'], Quiz.STATE_ACTIVE)
        self.assertEqual(quiz_data['answer'], self.quiz.answer)

    async def test_receive_success__review_quiz(self):

        # connect
        wsc, _ = await self.get_wsc(self.user)
        await wsc.receive_json_from()

        # activate lesson
        self.set_at(self.admin)
        url = reverse('app:api_instructor_lesson-activate', args=[
            self.lesson.seq,
        ])
        await self.aclient.post(url)
        await wsc.receive_json_from()

        # review quiz
        self.set_at(self.admin)
        url = reverse('app:api_instructor_quiz-review', args=[
            self.quiz.id,
        ])
        await self.aclient.post(url)

        # receive data
        data = await wsc.receive_json_from()
        self.assertEqual(
            data['type'],
            'instructor_live_quiz',
        )

        # check data
        quiz_data = data['quiz_data']
        self.assertEqual(quiz_data['id'], self.quiz.id)
        self.assertEqual(quiz_data['state'], Quiz.STATE_REVIEWING)
        self.assertEqual(quiz_data['answer'], self.quiz.answer)

    async def test_receive_success__close_quiz(self):

        # connect
        wsc, _ = await self.get_wsc(self.user)
        await wsc.receive_json_from()

        # activate lesson
        self.set_at(self.admin)
        url = reverse('app:api_instructor_lesson-activate', args=[
            self.lesson.seq,
        ])
        await self.aclient.post(url)
        await wsc.receive_json_from()

        # close quiz
        self.set_at(self.admin)
        url = reverse('app:api_instructor_quiz-close', args=[
            self.quiz.id,
        ])
        await self.aclient.post(url)

        # receive data
        data = await wsc.receive_json_from()
        self.assertEqual(
            data['type'],
            'instructor_live_quiz',
        )

        # check data
        quiz_data = data['quiz_data']
        self.assertIsNone(quiz_data)
