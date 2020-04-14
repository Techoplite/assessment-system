from django.conf import settings
from django.db import models


class Assessment(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    title = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.title} - ID: {self.id}'


class Problem(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    question = models.CharField(max_length=255, blank=False)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.question


class Answer(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    answer = models.CharField(max_length=255)
    question = models.ForeignKey(Problem, on_delete=models.CASCADE)
    is_correct_answer = models.BooleanField(default=False)

    def __str__(self):
        return self.answer


class AnswerGiven(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    question = models.ForeignKey(Problem, on_delete=models.CASCADE)
    student_answer = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f'Question: "{self.question}", Answer given: "{self.student_answer}", Correct answer: "{self.correct_answer}"'
