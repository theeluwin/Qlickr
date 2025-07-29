from django.urls import path

from app import consumers


websocket_urlpatterns = [
    path(
        'ws/instructor/',
        consumers.InstructorConsumer.as_asgi(),
        name='ws_instructor',
    ),
    path(
        'ws/student/',
        consumers.StudentConsumer.as_asgi(),
        name='ws_student',
    ),
]
