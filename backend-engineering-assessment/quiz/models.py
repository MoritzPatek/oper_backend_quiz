"""
This module contains the models for the Quiz application.

Written by: Moritz Patek | patekmoritz@yahoo.at
"""

from django.contrib.auth.models import User

from django.db import models


class Role(models.Model):
    """
    This model represents a user role.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.IntegerField(default=100)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    This model extends the User model to include a role field.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role.name else 'No Role'}"


class QuizStatus(models.Model):
    """
    This model represents the status of a quiz.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Quiz(models.Model):
    """
    This model represents a quiz.
    """

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quizzes_created")
    status = models.ForeignKey(QuizStatus, on_delete=models.CASCADE, related_name="quiz_status")
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.created_by} - {self.status}"


class Question(models.Model):
    """
    This model represents a question in a quiz.
    """

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]  # Ensures questions are fetched in creation order

    def __str__(self):
        return self.question


class Answer(models.Model):
    """
    This model represents an answer to a question.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.answer


class AssignedQuiz(models.Model):
    """
    This model represents a quiz assigned to a user.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_quizzes")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="assigned_users")
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quiz.title} - {self.user.username}"


class UserQuizProgress(models.Model):
    """
    This model represents a user's progress in a quiz.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_progresses")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="user_progresses")
    last_answered_question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True, related_name="last_answered_progress"
    )
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - Progress"


class AnsweredQuestion(models.Model):
    """
    This model represents a question that has been answered by a user.
    """

    progress = models.ForeignKey(UserQuizProgress, on_delete=models.CASCADE, related_name="answered_questions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, default=None)
    answered_correctly = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.progress.user.username} - {self.question.question} - {'Correct' if self.answered_correctly else 'Incorrect'}"
