from uuid import uuid4
from pathlib import Path

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    UserManager as BaseUserManager,
    AbstractUser,
)


def get_quiz_image_path(instance, fname):
    ext = fname.split('.')[-1]
    fname = '{}.{}'.format(uuid4(), ext)
    return Path('quiz') / fname


class UserManager(BaseUserManager):

    def get_queryset(self):
        return super().get_queryset().select_related('student')


class User(AbstractUser):

    objects = UserManager()


class Student(models.Model):

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='student',
        on_delete=models.CASCADE,
        verbose_name='User',
    )
    personal_sid = models.CharField(
        max_length=20,
        default='',
        verbose_name='Student ID',
        unique=True,
    )
    personal_name = models.CharField(
        max_length=40,
        default='',
        verbose_name='Name',
        db_index=True,
    )
    role_department = models.CharField(
        max_length=40,
        default='',
        blank=True,
        null=True,
        verbose_name='Department',
    )
    role_major = models.CharField(
        max_length=40,
        default='',
        blank=True,
        null=True,
        verbose_name='Major',
    )
    role_year = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name='Year',
    )
    course_is_retake = models.BooleanField(
        default=False,
        verbose_name='Retake',
    )
    course_is_dropout = models.BooleanField(
        default=False,
        verbose_name='Dropout',
    )
    eval_project1 = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Project 1 Score',
    )
    eval_project2 = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Project 2 Score',
    )
    eval_project3 = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Project 3 Score',
    )
    eval_midterm = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Midterm Score',
    )
    eval_finals = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Finals Score',
    )
    eval_quiz = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Quiz Score',
    )
    extra_note = models.TextField(
        default="",
        blank=True,
        null=True,
        verbose_name='Note',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    def __str__(self):
        return (
            f"[St {self.pk}]"
            " "
            f"{self.personal_name}"
            " "
            f"({self.role_major} {self.role_year})"
        )


class Lesson(models.Model):

    class Meta:
        ordering = (
            'seq',
        )
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'

    STATE_PENDING = 1
    STATE_ACTIVE = 2
    STATE_CLOSED = 3
    STATE_CHOICES = (
        (STATE_PENDING, 'Pending'),
        (STATE_ACTIVE, 'Active'),
        (STATE_CLOSED, 'Closed'),
    )

    seq = models.PositiveSmallIntegerField(
        verbose_name='No.',
        primary_key=True,
    )
    state = models.PositiveSmallIntegerField(
        default=STATE_PENDING,
        choices=STATE_CHOICES,
        verbose_name='State',
    )
    date = models.DateField(
        verbose_name='Date',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    def __str__(self):
        return (
            f"[Ls {self.pk}]"
            " "
            f"Lesson {self.seq}"
            " "
            f"<{self.date}>"
            " "
            f"({self.get_state_display()})"
        )


class Quiz(models.Model):

    class Meta:
        ordering = (
            'lesson',
            'order',
        )
        unique_together = (
            'lesson',
            'order',
        )
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    STATE_PENDING = 1
    STATE_ACTIVE = 2
    STATE_REVIEWING = 3
    STATE_CLOSED = 4
    STATE_CHOICES = (
        (STATE_PENDING, 'Pending'),
        (STATE_ACTIVE, 'Active'),
        (STATE_REVIEWING, 'Reviewing'),
        (STATE_CLOSED, 'Closed'),
    )

    lesson = models.ForeignKey(
        'Lesson',
        related_name='quizzes',
        verbose_name='Lesson',
        on_delete=models.CASCADE,
    )
    order = models.PositiveSmallIntegerField(
        verbose_name='Order',
    )
    answer = models.PositiveSmallIntegerField(
        verbose_name='Answer',
    )
    content = models.TextField(
        default="",
        null=True,
        blank=True,
        verbose_name='Content',
    )
    image = models.FileField(
        upload_to=get_quiz_image_path,
        null=True,
        blank=True,
        verbose_name='Image',
    )
    state = models.PositiveSmallIntegerField(
        default=STATE_PENDING,
        choices=STATE_CHOICES,
        verbose_name='State',
    )
    note = models.TextField(
        default="",
        blank=True,
        null=True,
        verbose_name='Note',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    def __str__(self):
        return (
            f"[Qz {self.pk}]"
            " "
            f"Lesson {self.lesson_id}"
            " / "
            f"Quiz {self.order}"
            " "
            f"({self.get_state_display()})"
        )

    @classmethod
    def get_live_quiz(cls, states):
        quiz = (
            cls.objects
            .select_related('lesson')
            .prefetch_related('options')
            .filter(
                lesson__state=Lesson.STATE_ACTIVE,
                state__in=states,
            ).order_by('lesson__seq', 'order')
            .first()
        )
        return quiz


class Option(models.Model):

    class Meta:
        ordering = (
            'quiz',
            'order',
        )
        unique_together = (
            'quiz',
            'order',
        )
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

    quiz = models.ForeignKey(
        'Quiz',
        related_name='options',
        verbose_name='Quiz',
        on_delete=models.CASCADE,
    )
    order = models.PositiveSmallIntegerField(
        verbose_name='Order',
    )
    content = models.TextField(
        default="",
        null=True,
        blank=True,
        verbose_name='Content',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    def __str__(self):
        return (
            f"[Op {self.pk}]"
            " "
            f"Lesson {self.quiz.lesson_id}"
            " / "
            f"Quiz {self.quiz.order}"
            " / "
            f"Option {self.order}"
        )


class Response(models.Model):

    class Meta:
        ordering = (
            '-created_at',
        )
        unique_together = (
            'user',
            'quiz',
        )
        verbose_name = 'Response'
        verbose_name_plural = 'Responses'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='responses',
        verbose_name='User',
        on_delete=models.CASCADE,
    )
    quiz = models.ForeignKey(
        'Quiz',
        related_name='responses',
        verbose_name='Quiz',
        on_delete=models.CASCADE,
    )
    option = models.ForeignKey(
        'Option',
        related_name='responses',
        verbose_name='Option',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    def __str__(self):
        return (
            f"[Rs {self.pk}]"
            " "
            f"Lesson {self.quiz.lesson_id}"
            " / "
            f"Quiz {self.quiz.order}"
            " / "
            f"User <{self.user.username}>"
            ": "
            f"Option {self.option.order}"
        )
