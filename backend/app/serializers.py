from math import ceil

from django.db import transaction
from django.core.cache import cache
from django.core.validators import validate_email
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from app.models import (
    Student,
    Lesson,
    Quiz,
    Option,
    Response,
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'is_staff',
        ]
        read_only_fields = [
            'is_staff',
        ]
        write_only_fields = [
            'password',
        ]

    username = serializers.EmailField(
        validators=[validate_email],
    )
    password = serializers.CharField(
        validators=[validate_password],
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        del data['password']
        return data

    def validate_username(self, value):
        user = self.context['user']
        if (
            User.objects
            .filter(username=value)
            .exclude(username=user.username)
            .exists()
        ):
            raise serializers.ValidationError("This email is already in use.")
        return value


class UserRegistrationSerializer(serializers.Serializer):

    username = serializers.EmailField(
        write_only=True,
        validators=[validate_email],
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
    )
    personal_sid = serializers.CharField(
        max_length=20,
        required=True,
    )
    personal_name = serializers.CharField(
        max_length=20,
        required=True,
    )
    role_department = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        default='',
    )
    role_major = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        default='',
    )
    role_year = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        max_value=2 ** 15 - 1,
    )

    def validate(self, attrs):

        # validate username
        username = attrs['username']
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This email is already in use.")

        # validate personal_sid
        personal_sid = attrs['personal_sid']
        if Student.objects.filter(personal_sid=personal_sid).exists():
            raise serializers.ValidationError("This student ID is already in use.")

        # validate password
        user = User(username=username, email=username)
        validate_password(attrs['password'], user)

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            user, _ = User.objects.get_or_create(
                username=validated_data['username'],
            )
            user.set_password(validated_data['password'])
            user.save()
            del validated_data['username']
            del validated_data['password']
            _, _ = Student.objects.get_or_create(
                user=user,
                defaults=validated_data,
            )
        return user


class PasswordRequestSerializer(serializers.Serializer):

    email = serializers.EmailField(
        validators=[validate_email],
        required=True,
    )

    def validate_email(self, value):
        ticket = cache.get(f'password_reset:email:{value}')
        ttl = cache.ttl(f'password_reset:email:{value}')
        if ticket is not None and ttl is not None and ttl > 0:
            raise serializers.ValidationError(
                f"This email is already requested. Please try again in {ceil(ttl / 60)} minutes.",
            )
        return value


class PasswordResetSerializer(serializers.Serializer):

    ticket = serializers.CharField(
        required=True,
    )
    password = serializers.CharField(
        validators=[validate_password],
        required=True,
    )

    def validate_ticket(self, value):
        email = cache.get(f'password_reset:ticket:{value}')
        ttl = cache.ttl(f'password_reset:ticket:{value}')
        if not email:
            raise serializers.ValidationError("Invalid token.")
        if ttl is None or ttl <= 0:
            raise serializers.ValidationError("Invalid token.")
        if not User.objects.filter(username=email).exists():
            raise serializers.ValidationError("Invalid token.")
        self.context['email'] = email
        return value


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            'personal_sid',
            'personal_name',
            'role_department',
            'role_major',
            'role_year',
            'eval_project1',
            'eval_project2',
            'eval_project3',
            'eval_midterm',
            'eval_finals',
            'eval_quiz',
            'quiz_count',
        ]
        read_only_fields = [
            'eval_project1',
            'eval_project2',
            'eval_project3',
            'eval_midterm',
            'eval_finals',
            'eval_quiz',
            'quiz_count',
        ]

    quiz_count = serializers.SerializerMethodField()

    def get_quiz_count(self, obj):
        return (
            Quiz.objects
            .select_related('lesson')
            .filter(
                lesson__state=Lesson.STATE_CLOSED,
                state=Quiz.STATE_CLOSED,
            )
            .count()
        )

    def validate_personal_sid(self, value):
        if (
            Student.objects
            .filter(personal_sid=value)
            .exclude(personal_sid=self.instance.personal_sid)
            .exists()
        ):
            raise serializers.ValidationError("This student ID is already in use.")
        return value


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = [
            'seq',
            'state',
            'date',
        ]
        read_only_fields = [
            'seq',
            'state',
            'date',
        ]


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = [
            'id',
            'order',
            'content',
        ]
        read_only_fields = [
            'id',
            'order',
            'content',
        ]


class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        fields = [
            'id',
            'lesson_id',
            'order',
            'answer',
            'content',
            'image_url',
            'state',
            'options',
        ]
        read_only_fields = [
            'id',
            'lesson_id',
            'order',
            'answer',
            'content',
            'image_url',
            'options',
        ]

    image_url = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    options = OptionSerializer(many=True)

    def get_answer(self, obj):
        if self.context.get('hide_answer', False):
            return None
        return obj.answer

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class ResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Response
        fields = [
            'id',
            'username',
            'quiz_id',
            'option_id',
            'option_order',
            'quiz',
            'option',
        ]
        read_only_fields = [
            'id',
            'username',
            'quiz_id',
            'option_id',
            'option_order',
        ]
        write_only_fields = [
            'quiz',
            'option',
        ]

    username = serializers.SerializerMethodField()
    quiz_id = serializers.SerializerMethodField()
    option_id = serializers.SerializerMethodField()
    option_order = serializers.SerializerMethodField()
    quiz = serializers.PrimaryKeyRelatedField(
        queryset=Quiz.objects.select_related('lesson').all(),
        write_only=True,
    )

    def get_username(self, obj):
        return obj.user.username

    def get_quiz_id(self, obj):
        return obj.quiz_id

    def get_option_id(self, obj):
        return obj.option_id

    def get_option_order(self, obj):
        return obj.option.order

    def validate(self, attrs):
        quiz = attrs.get('quiz')
        if quiz.lesson.state != Lesson.STATE_ACTIVE:
            raise serializers.ValidationError("Invalid quiz.")
        if quiz.state != Quiz.STATE_ACTIVE:
            raise serializers.ValidationError("Invalid quiz.")
        option = attrs.get('option')
        if option.quiz != quiz:
            raise serializers.ValidationError("Invalid option.")
        return attrs
