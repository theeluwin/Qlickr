from uuid import uuid4

from django.contrib.auth import get_user_model
from import_export import (
    resources,
    fields,
)
from import_export.widgets import (
    ForeignKeyWidget,
    DateWidget,
)

from app.models import (
    Student,
    Lesson,
    Quiz,
    Option,
    Response,
)


User = get_user_model()


class StudentResource(resources.ModelResource):

    class Meta:
        model = Student
        fields = (
            'user',
            'personal_sid',
            'personal_name',
            'role_department',
            'role_major',
            'role_year',
            'course_is_retake',
            'course_is_dropout',
            'eval_project1',
            'eval_project2',
            'eval_project3',
            'eval_midterm',
            'eval_finals',
            'eval_quiz',
            'extra_note',
        )
        import_id_fields = (
            'user',
        )

    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username'),
    )

    def before_import_row(self, row, **kwargs):
        username = row.get('user')
        user, created = User.objects.get_or_create(
            username=username,
        )
        if created:
            password = str(uuid4())
            user.set_password(password)
            user.save()


class LessonResource(resources.ModelResource):

    class Meta:
        model = Lesson
        fields = (
            'seq',
            'state',
            'date',
        )
        import_id_fields = (
            'seq',
        )

    date = fields.Field(
        column_name='date',
        attribute='date',
        widget=DateWidget(format='%Y-%m-%d'),
    )


class QuizResource(resources.ModelResource):

    class Meta:
        model = Quiz
        fields = (
            'id',
            'lesson',
            'order',
            'answer',
            'content',
            'state',
            'note',
        )

    lesson = fields.Field(
        column_name='lesson',
        attribute='lesson',
        widget=ForeignKeyWidget(Lesson, 'seq'),
    )


class OptionResource(resources.ModelResource):

    class Meta:
        model = Option
        fields = (
            'id',
            'quiz',
            'order',
            'content',
        )

    quiz = fields.Field(
        column_name='quiz',
        attribute='quiz',
        widget=ForeignKeyWidget(Quiz, 'id'),
    )


class ResponseResource(resources.ModelResource):

    class Meta:
        model = Response
        fields = (
            'id',
            'user',
            'quiz',
            'option',
        )

    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username'),
    )
    quiz = fields.Field(
        column_name='quiz',
        attribute='quiz',
        widget=ForeignKeyWidget(Quiz, 'id'),
    )
    option = fields.Field(
        column_name='option',
        attribute='option',
        widget=ForeignKeyWidget(Option, 'id'),
    )
