import logging

from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response as Res
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
)
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from app.authentication import Authentication
from app.models import (
    Lesson,
    Quiz,
    Response,
)
from app.serializers import (
    LessonSerializer,
    QuizSerializer,
    ResponseSerializer,
)
from app.consumers import (
    InstructorConsumer,
    StudentConsumer,
)


def broadcast_live_quiz_data(group_name, quiz_data):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'broadcast_live_quiz_data',
                'quiz_data': quiz_data,
            }
        )
    except Exception as e:
        logger = logging.getLogger('channels')
        logger.error(f"Failed to broadcast live quiz data: {e}")


class InstructorLessonViewSet(viewsets.ModelViewSet):

    model = Lesson
    queryset = Lesson.objects.order_by('seq')
    serializer_class = LessonSerializer
    authentication_classes = [Authentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ['get', 'post']
    filter_backends = [OrderingFilter]
    ordering_fields = ['seq', 'date']
    ordering = ['seq']

    def create(self, request, *args, **kwargs):
        return Res({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post'])
    def activate(self, request, *args, **kwargs):
        with transaction.atomic():
            lesson = self.get_object()
            Lesson.objects.filter(seq__lt=lesson.seq).update(
                state=Lesson.STATE_CLOSED,
            )
            Lesson.objects.filter(seq__gt=lesson.seq).update(
                state=Lesson.STATE_PENDING,
            )
            lesson.state = Lesson.STATE_ACTIVE
            lesson.save()
            Quiz.objects.filter(
                state__in=[
                    Quiz.STATE_ACTIVE,
                    Quiz.STATE_REVIEWING,
                ],
            ).update(state=Quiz.STATE_CLOSED)
        broadcast_live_quiz_data(
            InstructorConsumer.GROUP_NAME,
            None,
        )
        broadcast_live_quiz_data(
            StudentConsumer.GROUP_NAME,
            None,
        )
        return Res({
            'message': f"Lesson {lesson.seq} is activated."
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close(self, request, *args, **kwargs):
        lesson = self.get_object()
        with transaction.atomic():
            Lesson.objects.filter(seq__lt=lesson.seq).update(
                state=Lesson.STATE_CLOSED,
            )
            Lesson.objects.filter(seq__gt=lesson.seq).update(
                state=Lesson.STATE_PENDING,
            )
            lesson.state = Lesson.STATE_CLOSED
            lesson.save()
            Quiz.objects.filter(
                state__in=[
                    Quiz.STATE_ACTIVE,
                    Quiz.STATE_REVIEWING,
                ],
            ).update(state=Quiz.STATE_CLOSED)
        broadcast_live_quiz_data(
            StudentConsumer.GROUP_NAME,
            None,
        )
        broadcast_live_quiz_data(
            InstructorConsumer.GROUP_NAME,
            None,
        )
        return Res({
            'message': f"Lesson {lesson.seq} is closed."
        }, status=status.HTTP_200_OK)


class InstructorQuizViewSet(viewsets.ModelViewSet):

    model = Quiz
    queryset = (
        Quiz.objects
        .select_related('lesson')
        .prefetch_related('options')
        .filter(
            lesson__state=Lesson.STATE_ACTIVE,
        )
        .order_by('lesson', 'order')
    )
    serializer_class = QuizSerializer
    authentication_classes = [Authentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ['get', 'post']
    filter_backends = [OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']

    def create(self, request, *args, **kwargs):
        return Res({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post'])
    def activate(self, request, *args, **kwargs):
        quiz = self.get_object()
        with transaction.atomic():
            Quiz.objects.filter(
                lesson=quiz.lesson,
                order__lt=quiz.order,
            ).update(state=Quiz.STATE_CLOSED)
            Quiz.objects.filter(
                lesson=quiz.lesson,
                order__gt=quiz.order,
            ).update(state=Quiz.STATE_PENDING)
            quiz.state = Quiz.STATE_ACTIVE
            quiz.save()
        instructor_quiz_data = QuizSerializer(quiz).data
        student_quiz_data = QuizSerializer(
            instance=quiz,
            context={
                'hide_answer': True,
            },
        ).data
        broadcast_live_quiz_data(
            InstructorConsumer.GROUP_NAME,
            instructor_quiz_data,
        )
        broadcast_live_quiz_data(
            StudentConsumer.GROUP_NAME,
            student_quiz_data,
        )
        return Res({
            'message': f"Quiz {quiz.order} is activated."
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def review(self, request, *args, **kwargs):
        quiz = self.get_object()
        with transaction.atomic():
            Quiz.objects.filter(
                lesson=quiz.lesson,
                order__lt=quiz.order,
            ).update(state=Quiz.STATE_CLOSED)
            Quiz.objects.filter(
                lesson=quiz.lesson,
                order__gt=quiz.order,
            ).update(state=Quiz.STATE_PENDING)
            quiz.state = Quiz.STATE_REVIEWING
            quiz.save()
        instructor_quiz_data = QuizSerializer(quiz).data
        broadcast_live_quiz_data(
            InstructorConsumer.GROUP_NAME,
            instructor_quiz_data,
        )
        broadcast_live_quiz_data(
            StudentConsumer.GROUP_NAME,
            None,
        )
        return Res({
            'message': f"Starting to review Quiz {quiz.order}."
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close(self, request, *args, **kwargs):
        quiz = self.get_object()
        with transaction.atomic():
            Quiz.objects.filter(
                lesson=quiz.lesson,
                order__lt=quiz.order,
            ).update(state=Quiz.STATE_CLOSED)
            Quiz.objects.filter(
                lesson=quiz.lesson,
                order__gt=quiz.order,
            ).update(state=Quiz.STATE_PENDING)
            quiz.state = Quiz.STATE_CLOSED
            quiz.save()
        broadcast_live_quiz_data(
            InstructorConsumer.GROUP_NAME,
            None,
        )
        broadcast_live_quiz_data(
            StudentConsumer.GROUP_NAME,
            None,
        )
        return Res({
            'message': f"Quiz {quiz.order} is closed."
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def results(self, request, *args, **kwargs):
        quiz = self.get_object()
        if quiz.state != Quiz.STATE_REVIEWING:
            return Res({
                'message': f"Quiz {quiz.order} is not under review."
            }, status=status.HTTP_400_BAD_REQUEST)
        options = (
            quiz.options
            .prefetch_related('responses')
            .order_by('order')
        )
        orders = []
        counts = []
        for option in options:
            orders.append(option.order)
            counts.append(option.responses.count())
        total = Response.objects.filter(quiz=quiz).count()
        return Res({
            'orders': orders,
            'counts': counts,
            'total': total,
        }, status=status.HTTP_200_OK)


class StudentResponseViewSet(viewsets.ModelViewSet):

    model = Response
    serializer_class = ResponseSerializer
    authentication_classes = [Authentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz']

    def get_queryset(self):
        Q_user = Q(user=self.request.user)
        Q_lesson = Q(
            quiz__lesson__state=Lesson.STATE_ACTIVE,
        )
        Q_quiz = Q(
            quiz__state=Quiz.STATE_ACTIVE,
        )
        return (
            Response.objects
            .select_related(
                'user',
                'user__student',
                'quiz',
                'quiz__lesson',
            )
            .filter(
                Q_user,
                Q_lesson,
                Q_quiz,
            )
        )

    def perform_create(self, serializer):
        quiz = serializer.validated_data['quiz']
        option = serializer.validated_data['option']
        response, _ = Response.objects.update_or_create(
            user=self.request.user,
            quiz=quiz,
            defaults={
                'option': option,
            },
        )
        serializer.instance = response
