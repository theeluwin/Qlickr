from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from app.models import (
    Student,
    Lesson,
    Quiz,
    Option,
    Response,
)
from app.resources import (
    StudentResource,
    LessonResource,
    QuizResource,
    OptionResource,
    ResponseResource,
)


User = get_user_model()


def ellipsis(text, length=10):
    if len(text) > length:
        return f"\"{text[:length]}…\""
    else:
        return f"\"{text}\""


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    pass


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):

    resource_class = StudentResource

    list_display = (
        'user',
        'verbose_summary',
        'personal_sid',
        'personal_name',
        'role_department',
        'role_major',
        'role_year',
        'course_is_retake',
        'course_is_dropout',
        'extra_note',
    )
    list_filter = (
        'role_department',
        'role_major',
        'role_year',
        'course_is_retake',
        'course_is_dropout',
    )
    ordering = (
        '-created_at',
    )
    search_fields = (
        'user__username',
        'personal_sid',
        'personal_name',
        'role_department',
        'role_major',
        'extra_note',
    )

    readonly_fields = (
        'verbose_summary',
        'created_at',
        'updated_at',
    )
    raw_id_fields = (
        'user',
    )
    fieldsets = (
        ('Verbose', {
            'fields': (
                'verbose_summary',
            ),
        }),
        ('Details', {
            'fields': (
                'user',
            ),
        }),
        ('Personal', {
            'fields': (
                'personal_sid',
                'personal_name',
            ),
        }),
        ('Role', {
            'fields': (
                'role_department',
                'role_major',
                'role_year',
            ),
        }),
        ('Course', {
            'fields': (
                'course_is_retake',
                'course_is_dropout',
            ),
        }),
        ('Eval', {
            'fields': (
                'eval_project1',
                'eval_project2',
                'eval_project3',
                'eval_midterm',
                'eval_finals',
                'eval_quiz',
            ),
        }),
        ('Extra', {
            'fields': (
                'extra_note',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': (
                'collapse',
            ),
        }),
    )

    def verbose_summary(self, obj):
        if obj.pk:
            return str(obj)
        else:
            return "-"
    verbose_summary.short_description = 'Summary'


@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):

    resource_class = LessonResource

    ordering = (
        'seq',
        'date',
    )
    list_display = (
        'seq',
        'verbose_summary',
        'state',
        'date',
    )
    list_filter = (
        'state',
    )
    list_editable = (
        'state',
    )
    search_fields = (
        'seq',
    )

    readonly_fields = (
        'verbose_summary',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        ('Verbose', {
            'fields': (
                'verbose_summary',
            ),
        }),
        ('Details', {
            'fields': (
                'seq',
                'date',
            ),
        }),
        ('Status', {
            'fields': (
                'state',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': (
                'collapse',
            ),
        }),
    )

    def verbose_summary(self, obj):
        if obj.pk:
            return str(obj)
        else:
            return "-"
    verbose_summary.short_description = 'Summary'


class OptionInline(admin.StackedInline):

    model = Option
    extra = 0
    min_num = 2
    ordering = (
        'order',
    )
    fields = (
        'order',
        'content',
    )


@admin.register(Quiz)
class QuizAdmin(ImportExportModelAdmin):

    resource_class = QuizResource

    ordering = (
        'lesson',
        'order',
    )
    list_display = (
        'id',
        'verbose_image',
        'verbose_summary',
        'lesson',
        'order',
        'answer',
        'state',
    )
    list_filter = (
        'lesson',
        'state',
    )
    list_editable = (
        'order',
        'answer',
        'state',
    )
    search_fields = (
        'quiz_id',
    )

    inlines = (
        OptionInline,
    )
    readonly_fields = (
        'verbose_image',
        'verbose_summary',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        ('Verbose', {
            'fields': (
                'verbose_image',
                'verbose_summary',
            ),
        }),
        ('Details', {
            'fields': (
                'lesson',
                'order',
                'answer',
                'content',
                'image',
            ),
        }),
        ('Status', {
            'fields': (
                'state',
            ),
        }),
        ('Extra', {
            'fields': (
                'note',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': (
                'collapse',
            ),
        }),
    )

    def verbose_summary(self, obj):
        if obj.pk:
            return str(obj)
        else:
            return "-"
    verbose_summary.short_description = 'Summary'

    def verbose_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px;" />',
                obj.image.url,
            )
        return "-"
    verbose_image.short_description = 'Preview'


@admin.register(Option)
class OptionAdmin(ImportExportModelAdmin):

    resource_class = OptionResource

    ordering = (
        'quiz',
        'order',
    )
    list_display = (
        'id',
        'verbose_summary',
        'quiz',
        'order',
    )
    list_filter = (
        'quiz__lesson',
    )
    list_editable = (
        'order',
    )
    search_fields = (
        'quiz_id',
    )

    readonly_fields = (
        'verbose_summary',
        'created_at',
        'updated_at',
    )
    raw_id_fields = (
        'quiz',
    )
    fieldsets = (
        ('Verbose', {
            'fields': (
                'verbose_summary',
            ),
        }),
        ('Details', {
            'fields': (
                'quiz',
                'order',
                'content',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': (
                'collapse',
            ),
        }),
    )

    def verbose_summary(self, obj):
        if obj.pk:
            return str(obj)
        else:
            return "-"
    verbose_summary.short_description = 'Summary'


@admin.register(Response)
class ResponseAdmin(ImportExportModelAdmin):

    resource_class = ResponseResource

    ordering = (
        '-created_at',
    )
    list_display = (
        'id',
        'user',
        'verbose_summary',
        'quiz',
        'option',
    )
    search_fields = (
        'user__profile__personal_name',
    )
    readonly_fields = (
        'verbose_summary',
        'created_at',
        'updated_at',
    )
    raw_id_fields = (
        'user',
        'quiz',
        'option',
    )
    fieldsets = (
        ('Verbose', {
            'fields': (
                'verbose_summary',
            ),
        }),
        ('Details', {
            'fields': (
                'user',
                'quiz',
                'option',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': (
                'collapse',
            ),
        }),
    )

    def verbose_summary(self, obj):
        if obj.pk:
            return str(obj)
        else:
            return "-"
    verbose_summary.short_description = 'Summary'
