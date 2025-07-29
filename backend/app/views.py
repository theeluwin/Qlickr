from uuid import uuid4
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response as Res
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)

from app.authentication import Authentication
from app.models import (
    Quiz,
    Student,
    Response,
)
from app.tasks import send_email
from app.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PasswordRequestSerializer,
    PasswordResetSerializer,
    StudentSerializer,
    QuizSerializer,
    ResponseSerializer,
)


AUTH_COOKIE_ACCESS = settings.SIMPLE_JWT['AUTH_COOKIE_ACCESS']
AUTH_COOKIE_REFRESH = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']

User = get_user_model()


def require_student(func):

    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'student') or not user.student:
            return Res({
                'error': "Student information not found.",
            }, status=status.HTTP_404_NOT_FOUND)
        return func(self, request, *args, student=user.student, **kwargs)

    return wrapper


class APITokenLoginView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        response_super = super().post(request, *args, **kwargs)
        res = Res({}, status=status.HTTP_200_OK)
        res.set_cookie(
            AUTH_COOKIE_REFRESH,
            response_super.data.get('refresh', None),
            httponly=True,
        )
        res.set_cookie(
            AUTH_COOKIE_ACCESS,
            response_super.data.get('access', None),
            httponly=True,
        )
        return res


class APITokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(AUTH_COOKIE_REFRESH, '')
        data = {
            'refresh': refresh,
        }
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        token = serializer.validated_data
        res = Res({}, status=status.HTTP_200_OK)
        res.set_cookie(
            AUTH_COOKIE_REFRESH,
            token['refresh'],
            httponly=True,
        )
        res.set_cookie(
            AUTH_COOKIE_ACCESS,
            token['access'],
            httponly=True,
        )
        return res


class APITokenLogoutView(TokenBlacklistView):

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(AUTH_COOKIE_REFRESH, '')
        data = {
            'refresh': refresh,
        }
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        res = Res({}, status=status.HTTP_200_OK)
        res.delete_cookie(AUTH_COOKIE_REFRESH)
        res.delete_cookie(AUTH_COOKIE_ACCESS)
        return res


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_health(request):
    return Res({})


@api_view(['POST'])
@authentication_classes([Authentication])
@permission_classes([IsAuthenticated])
def api_websocket_ticket(request):
    ticket = str(uuid4())
    user_id = request.user.id
    cache.set(
        f'websocket:ticket:{ticket}',
        user_id,
        settings.WEBSOCKET_TICKET_TTL,
    )
    return Res({
        'ticket': ticket,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_user_register(request):
    serializer = UserRegistrationSerializer(
        data=request.data,
    )
    if serializer.is_valid():
        _ = serializer.save()
        return Res({
            'message': "Registration completed."
        }, status=status.HTTP_201_CREATED)
    error = "Registration failed."
    for _, values in serializer.errors.items():
        for error in values:
            break
    return Res({
        'error': error,
    }, status=status.HTTP_400_BAD_REQUEST)


class APIUserMeView(APIView):

    authentication_classes = [Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Res(serializer.data)

    def patch(self, request):
        user = request.user
        if 'username' in request.data:
            serializer = UserSerializer(
                data=request.data,
                context={
                    'user': request.user,
                },
                partial=True,
            )
            if serializer.is_valid():
                user.username = serializer.validated_data['username']
                user.save()
                return Res({
                    'message': "Email changed successfully.",
                })
            return Res({
                'error': serializer.errors['username'][0]
            }, status=status.HTTP_400_BAD_REQUEST)
        if 'password' in request.data:
            serializer = UserSerializer(
                data=request.data,
                context={
                    'user': request.user,
                },
                partial=True,
            )
            if serializer.is_valid():
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Res({
                    'message': "Password changed successfully."
                })
            return Res({
                'error': serializer.errors['password'][0]
            }, status=status.HTTP_400_BAD_REQUEST)
        return Res({
            'error': "Please provide the information to change."
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_user_password_request(request):
    serializer = PasswordRequestSerializer(
        data=request.data,
    )
    if serializer.is_valid():
        email = serializer.validated_data['email']
        ticket = str(uuid4())
        cache.set(
            f'password_reset:email:{email}',
            ticket,
            settings.EMAIL_RETRY_DELAY,
        )
        if User.objects.filter(username=email).exists():
            cache.set(
                f'password_reset:ticket:{ticket}',
                email,
                settings.EMAIL_RETRY_DELAY,
            )
            link_href = (
                f"{settings.PROTOCOL}://{settings.HOST}"
                f"/password/reset?ticket={ticket}"
            )
            link_content = "Reset password"
            html_message = render_to_string(
                'email/password_request.html', {
                    'link_href': link_href,
                    'link_content': link_content,
                },
            )
            send_email.delay(
                f"[{settings.SITE_TITLE}] Reset password link",
                f"Reset password link: {link_href}",
                settings.EMAIL_HOST_USER,
                [email],
                html_message=html_message,
            )
        return Res({
            'message': "Reset password link sent to email."
        }, status=status.HTTP_201_CREATED)
    error = "Failed to send reset password link."
    for _, values in serializer.errors.items():
        for error in values:
            break
    return Res({
        'error': error,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_user_password_reset(request):
    serializer = PasswordResetSerializer(
        data=request.data,
    )
    if serializer.is_valid():
        ticket = serializer.validated_data['ticket']
        password = serializer.validated_data['password']
        email = serializer.context['email']
        user = User.objects.get(username=email)
        user.set_password(password)
        user.save()
        cache.delete(f'password_reset:email:{email}')
        cache.delete(f'password_reset:ticket:{ticket}')
        return Res({
            'message': "Password changed successfully."
        }, status=status.HTTP_200_OK)
    error = "Failed to reset password."
    for _, values in serializer.errors.items():
        for error in values:
            break
    return Res({
        'error': error,
    }, status=status.HTTP_400_BAD_REQUEST)


class APIStudentMeView(APIView):

    authentication_classes = [Authentication]
    permission_classes = [IsAuthenticated]

    @require_student
    def get(self, request, student=None):
        serializer = StudentSerializer(student)
        return Res(serializer.data)

    @require_student
    def patch(self, request, student=None):
        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Res(serializer.data)
        error = "Failed to update student information."
        for _, values in serializer.errors.items():
            for error in values:
                break
        return Res({
            'error': error,
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_instructor_dashboard(request):
    data = []
    quiz = Quiz.get_live_quiz([
        Quiz.STATE_ACTIVE,
        Quiz.STATE_REVIEWING,
    ])
    if not quiz:
        return Res({
            'quiz': None,
            'data': [],
        })
    students = (
        Student.objects
        .select_related('user')
        .order_by('personal_sid')
    )
    for student in students:
        student_data = StudentSerializer(student).data
        try:
            response = (
                Response.objects
                .select_related('option')
                .get(user=student.user, quiz=quiz)
            )
            response_data = ResponseSerializer(response).data
        except Response.DoesNotExist:
            response_data = None
        data.append({
            'student': student_data,
            'response': response_data,
        })
    return Res({
        'quiz': QuizSerializer(quiz).data,
        'data': data,
    })
