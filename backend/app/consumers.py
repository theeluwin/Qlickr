import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class InstructorConsumer(AsyncWebsocketConsumer):

    GROUP_NAME = 'instructor_group'

    async def connect(self):
        if not self.scope['user_data']['is_staff']:
            await self.close(code=4003)
            return
        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )
        await self.accept()
        quiz_data = await self.get_live_quiz_data()
        await self.broadcast_live_quiz_data({
            'quiz_data': quiz_data,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )

    async def broadcast_live_quiz_data(self, event):
        quiz_data = event['quiz_data']
        await self.send(text_data=json.dumps({
            'type': 'instructor_live_quiz',
            'quiz_data': quiz_data,
        }))

    @database_sync_to_async
    def get_live_quiz_data(self):
        from app.models import Quiz  # noqa: F401
        from app.serializers import QuizSerializer  # noqa: F401
        quiz = Quiz.get_live_quiz([
            Quiz.STATE_ACTIVE,
            Quiz.STATE_REVIEWING,
        ])
        if quiz:
            return QuizSerializer(quiz).data
        return None


class StudentConsumer(AsyncWebsocketConsumer):

    GROUP_NAME = 'student_group'

    async def connect(self):
        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )
        await self.accept()
        quiz_data = await self.get_live_quiz_data()
        await self.broadcast_live_quiz_data({
            'quiz_data': quiz_data,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )

    async def broadcast_live_quiz_data(self, event):
        quiz_data = event['quiz_data']
        await self.send(text_data=json.dumps({
            'type': 'student_live_quiz',
            'quiz_data': quiz_data,
        }))

    @database_sync_to_async
    def get_live_quiz_data(self):
        from app.models import Quiz  # noqa: F401
        from app.serializers import QuizSerializer  # noqa: F401
        quiz = Quiz.get_live_quiz([
            Quiz.STATE_ACTIVE,
        ])
        if quiz:
            return QuizSerializer(
                instance=quiz,
                context={
                    'hide_answer': True,
                },
            ).data
        return None
