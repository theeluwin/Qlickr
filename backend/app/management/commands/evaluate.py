from django.core.management.base import BaseCommand

from app.models import (
    Student,
    Lesson,
    Quiz,
    Response,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        students = Student.objects.all()
        quizzes = Quiz.objects.filter(
            lesson__state=Lesson.STATE_CLOSED,
        )
        for student in students:
            user = student.user
            student.eval_quiz = 0
            for quiz in quizzes:
                response = Response.objects.filter(
                    user=user,
                    quiz=quiz,
                ).first()
                if not response:
                    continue
                if response.option.order == quiz.answer:
                    student.eval_quiz += 1
                student.save()
        self.stdout.write(
            self.style.SUCCESS(f"Evaluated {students.count()} students")
        )
