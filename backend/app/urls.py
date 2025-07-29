from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from app import (
    views,
    viewsets,
)


router = DefaultRouter()
router.register(
    'instructor/lessons',
    viewsets.InstructorLessonViewSet,
    basename='api_instructor_lesson',
)
router.register(
    'instructor/quizzes',
    viewsets.InstructorQuizViewSet,
    basename='api_instructor_quiz',
)
router.register(
    'student/responses',
    viewsets.StudentResponseViewSet,
    basename='api_student_response',
)

urlpatterns = [
    path(
        'token/login/',
        views.APITokenLoginView.as_view(),
        name='api_token_login',
    ),
    path(
        'token/refresh/',
        views.APITokenRefreshView.as_view(),
        name='api_token_refresh',
    ),
    path(
        'token/logout/',
        views.APITokenLogoutView.as_view(),
        name='api_token_logout',
    ),
    path(
        'health/',
        views.api_health,
        name='api_health',
    ),
    path(
        'websocket/ticket/',
        views.api_websocket_ticket,
        name='api_websocket_ticket',
    ),
    path(
        'user/register/',
        views.api_user_register,
        name='api_user_register',
    ),
    path(
        'user/me/',
        views.APIUserMeView.as_view(),
        name='api_user_me',
    ),
    path(
        'user/password/request/',
        views.api_user_password_request,
        name='api_user_password_request',
    ),
    path(
        'user/password/reset/',
        views.api_user_password_reset,
        name='api_user_password_reset',
    ),
    path(
        'instructor/dashboard/',
        views.api_instructor_dashboard,
        name='api_instructor_dashboard',
    ),
    path(
        'student/me/',
        views.APIStudentMeView.as_view(),
        name='api_student_me',
    ),
    path(
        '',
        include(router.urls),
    ),
]
