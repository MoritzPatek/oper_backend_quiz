"""
This module contains all the tests for the API endpoints in the quiz app.

Written by: Moritz Patek | patekmoritz@yahoo.at
"""

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from .models import AnsweredQuestion
from .models import UserQuizProgress
from .models import AssignedQuiz
from .models import UserProfile
from .models import QuizStatus
from .models import Question
from .models import Answer
from .models import Role
from .models import Quiz


from django.urls import reverse


class CreateUserTests(TestCase):
    def setUp(self):
        # Create a role to use in the tests
        self.role = Role.objects.create(name="TestRole")
        self.client = APIClient()

        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@email.com", password="adminpassword"
        )

        # The URL for the create_user endpoint
        self.url = reverse("create_user")

    def test_create_user(self):
        # Authenticate as the superuser
        self.client.login(username="admin", password="adminpassword")

        # Create a user with the role
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "password": "testpassword",
                "email": "test@email.com",
                "role": self.role.name,
            },
            format="json",
        )

        # Check that the user was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # 1 superuser + 1 new user

    def test_create_user_unauthenticated(self):
        # Try to create a user without authentication
        response = self.client.post(
            self.url,
            {
                "username": "unauthuser",
                "password": "password123",
                "email": "unauthuser@email.com",
                "role": self.role.name,
            },
            format="json",
        )

        # Check that the request was unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.count(), 1)  # Only the superuser exists


class CreateQuizTests(TestCase):
    def setUp(self):
        # Create the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can create quizzes", level=1)

        # Create a user with the Creator role
        self.creator_user = User.objects.create_user(
            username="creatoruser", password="password123", email="creator@example.com"
        )
        UserProfile.objects.create(user=self.creator_user, role=self.creator_role)

        # Create a user without the Creator role
        self.other_user = User.objects.create_user(
            username="otheruser", password="password123", email="other@example.com"
        )

        self.client = APIClient()

        # Create a quiz status
        self.quiz_status = QuizStatus.objects.create(name="Draft", description="Quiz is in draft state")

        # The URL for the create_quiz endpoint
        self.url = reverse("create_quiz")

    def test_create_quiz_as_creator(self):
        # Authenticate as the creator user
        self.client.login(username="creatoruser", password="password123")

        # Data for creating a quiz
        data = {
            "title": "Sample Quiz",
            "description": "This is a sample quiz",
        }

        # Create the quiz
        response = self.client.post(self.url, data, format="json")

        # Check that the quiz was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Quiz.objects.get().title, "Sample Quiz")
        self.assertEqual(Quiz.objects.get().created_by, self.creator_user)

    def test_create_quiz_without_creator_role(self):
        # Authenticate as a user without the Creator role
        self.client.login(username="otheruser", password="password123")

        # Data for creating a quiz
        data = {
            "title": "Unauthorized Quiz",
            "description": "This should not be created",
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Quiz.objects.count(), 0)


class CreateQuestionTests(TestCase):
    def setUp(self):
        # Create the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can create quizzes and questions", level=1)

        # Create a user with the Creator role
        self.creator_user = User.objects.create_user(
            username="creatoruser", password="password123", email="creator@example.com"
        )
        UserProfile.objects.create(user=self.creator_user, role=self.creator_role)

        # Create a user without the Creator role
        self.other_user = User.objects.create_user(
            username="otheruser", password="password123", email="other@example.com"
        )

        self.client = APIClient()

        # Create a quiz status and a quiz to add questions to
        self.quiz_status = QuizStatus.objects.create(name="Draft", description="Quiz is in draft state")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz",
            description="This is a sample quiz",
            created_by=self.creator_user,
            status=self.quiz_status,
        )

        # The URL for the create_question endpoint
        self.url = reverse("create_question")

    def test_create_question_as_creator(self):
        # Authenticate as the creator user
        self.client.login(username="creatoruser", password="password123")

        # Data for creating a question
        data = {
            "question": "What is the capital of France?",
            "quiz_id": self.quiz.id,
        }

        # Create the question
        response = self.client.post(self.url, data, format="json")

        # Check that the question was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Question.objects.get().question, "What is the capital of France?")
        self.assertEqual(Question.objects.get().quiz, self.quiz)

    def test_create_question_without_creator_role(self):
        # Authenticate as a user without the Creator role
        self.client.login(username="otheruser", password="password123")

        # Data for creating a question
        data = {
            "question": "What is the capital of France?",
            "quiz_id": self.quiz.id,
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Question.objects.count(), 0)


class CreateAnswerTests(TestCase):
    def setUp(self):
        # Create the Creator role
        self.creator_role = Role.objects.create(
            name="Creator", description="Can create quizzes, questions, and answers", level=1
        )

        # Create a user with the Creator role
        self.creator_user = User.objects.create_user(
            username="creatoruser", password="password123", email="creator@example.com"
        )
        UserProfile.objects.create(user=self.creator_user, role=self.creator_role)

        # Create a user without the Creator role
        self.other_user = User.objects.create_user(
            username="otheruser", password="password123", email="other@example.com"
        )

        self.client = APIClient()

        # Create a quiz status, a quiz, and a question to add answers to
        self.quiz_status = QuizStatus.objects.create(name="Draft", description="Quiz is in draft state")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz",
            description="This is a sample quiz",
            created_by=self.creator_user,
            status=self.quiz_status,
        )
        self.question = Question.objects.create(quiz=self.quiz, question="What is the capital of France?")

        # The URL for the create_answer endpoint
        self.url = reverse("create_answer")

    def test_create_answer_as_creator(self):
        # Authenticate as the creator user
        self.client.login(username="creatoruser", password="password123")

        # Data for creating an answer
        data = {
            "answer": "Paris",
            "is_correct": True,
            "question_id": self.question.id,
        }

        # Create the answer
        response = self.client.post(self.url, data, format="json")

        # Check that the answer was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 1)
        self.assertEqual(Answer.objects.get().answer, "Paris")
        self.assertEqual(Answer.objects.get().question, self.question)

    def test_create_answer_by_non_creator_of_quiz(self):
        # Authenticate as a user without the Creator role or as a creator not owning the quiz
        self.client.login(username="otheruser", password="password123")

        # Data for creating an answer
        data = {
            "answer": "Paris",
            "is_correct": True,
            "question_id": self.question.id,
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Answer.objects.count(), 0)


class CreateAnsweredQuestionTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        self.client = APIClient()

        # Create a quiz status, a quiz, and a question
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz",
            description="This is a sample quiz",
            created_by=self.user,
            status=self.quiz_status,
        )
        self.question = Question.objects.create(quiz=self.quiz, question="What is the capital of France?")
        self.answer = Answer.objects.create(
            question=self.question,
            answer="Paris",
            is_correct=True,
        )

        # Create a user quiz progress
        self.user_progress = UserQuizProgress.objects.create(
            user=self.user,
            quiz=self.quiz,
        )

        # The URL for the create_answered_question endpoint
        self.url = reverse("create_answered_question")

    def test_create_answered_question(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Data for creating an answered question
        data = {
            "question_id": self.question.id,
            "answer_id": self.answer.id,
        }

        # Create the answered question
        response = self.client.post(self.url, data, format="json")

        # Check that the answered question was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AnsweredQuestion.objects.count(), 1)
        self.assertEqual(AnsweredQuestion.objects.get().question, self.question)
        self.assertEqual(AnsweredQuestion.objects.get().answer, self.answer)

    def test_create_answered_question_with_nonexistent_question(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Data with a non-existent question ID
        data = {
            "question_id": 999,  # This question does not exist
            "answer_id": self.answer.id,
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request returned a 404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Question does not exist.")

    def test_create_answered_question_with_nonexistent_answer(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Data with a non-existent answer ID
        data = {
            "question_id": self.question.id,
            "answer_id": 999,  # This answer does not exist
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request returned a 404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Answer does not exist.")


class SetQuizToUserTests(TestCase):
    def setUp(self):
        # Create the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can assign quizzes", level=1)

        # Create a user with the Creator role
        self.creator_user = User.objects.create_user(
            username="creatoruser", password="password123", email="creator@example.com"
        )
        UserProfile.objects.create(user=self.creator_user, role=self.creator_role)

        # Create another user to assign quizzes to
        self.target_user = User.objects.create_user(
            username="targetuser", password="password123", email="targetuser@example.com"
        )

        self.client = APIClient()

        # Create a quiz status and a quiz to be assigned
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz",
            description="This is a sample quiz",
            created_by=self.creator_user,
            status=self.quiz_status,
        )

        # The URL for the set_quiz_to_user endpoint
        self.url = reverse("set_quiz_to_user")

    def test_set_quiz_to_user(self):
        # Authenticate as the creator user
        self.client.login(username="creatoruser", password="password123")

        # Data for assigning the quiz to a user
        data = {
            "quiz_id": self.quiz.id,
            "user_id": self.target_user.id,
        }

        # Assign the quiz to the user
        response = self.client.post(self.url, data, format="json")

        # Check that the assignment was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AssignedQuiz.objects.count(), 1)
        self.assertEqual(AssignedQuiz.objects.get().quiz, self.quiz)
        self.assertEqual(AssignedQuiz.objects.get().user, self.target_user)

    def test_set_quiz_to_user_when_already_assigned(self):
        # Authenticate as the creator user
        self.client.login(username="creatoruser", password="password123")

        # Assign the quiz to the user the first time
        AssignedQuiz.objects.create(user=self.target_user, quiz=self.quiz)

        # Attempt to assign the quiz again to the same user
        data = {
            "quiz_id": self.quiz.id,
            "user_id": self.target_user.id,
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request was rejected because the quiz was already assigned
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "User already assigned to the quiz.")

    def test_set_quiz_to_user_with_nonexistent_quiz(self):
        # Authenticate as the creator user
        self.client.login(username="creatoruser", password="password123")

        # Data with a non-existent quiz ID
        data = {
            "quiz_id": 999,  # This quiz does not exist
            "user_id": self.target_user.id,
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request returned a 404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Quiz does not exist.")

    def test_set_quiz_to_user_with_nonexistent_user(self):
        # Authenticate as the creator user
        self.client.login(username="creatoruser", password="password123")

        # Data with a non-existent user ID
        data = {
            "quiz_id": self.quiz.id,
            "user_id": 999,  # This user does not exist
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request returned a 404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User does not exist.")


class SetAcceptedStatusTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        self.client = APIClient()

        # Create a quiz status and a quiz
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz",
            description="This is a sample quiz",
            created_by=self.user,
            status=self.quiz_status,
        )

        # Assign the quiz to the user
        self.assigned_quiz = AssignedQuiz.objects.create(user=self.user, quiz=self.quiz)

        # The URL for the set_accepted_status endpoint
        self.url = reverse("set_accepted_status")

    def test_set_accepted_status_to_true(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Data to set the accepted status to True
        data = {
            "quiz_id": self.quiz.id,
            "accepted": True,
        }

        # Update the accepted status
        response = self.client.post(self.url, data, format="json")

        # Check that the status was updated successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assigned_quiz.refresh_from_db()
        self.assertTrue(self.assigned_quiz.accepted)
        self.assertEqual(UserQuizProgress.objects.count(), 1)

    def test_set_accepted_status_to_false(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # First set the status to accepted (True)
        UserQuizProgress.objects.create(user=self.user, quiz=self.quiz)
        self.assigned_quiz.accepted = True
        self.assigned_quiz.save()

        # Data to set the accepted status to False
        data = {
            "quiz_id": self.quiz.id,
            "accepted": False,
        }

        # Update the accepted status
        response = self.client.post(self.url, data, format="json")

        # Check that the status was updated successfully and progress was removed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assigned_quiz.refresh_from_db()
        self.assertFalse(self.assigned_quiz.accepted)
        self.assertEqual(UserQuizProgress.objects.count(), 0)

    def test_set_accepted_status_with_nonexistent_quiz(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Data with a non-existent quiz ID
        data = {
            "quiz_id": 999,  # This quiz does not exist
            "accepted": True,
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request returned a 404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Quiz does not exist.")

    def test_set_accepted_status_for_unassigned_quiz(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Create another quiz not assigned to the user
        other_quiz = Quiz.objects.create(
            title="Other Quiz",
            description="This quiz is not assigned to the user",
            created_by=self.user,
            status=self.quiz_status,
        )

        # Data to set the accepted status for the unassigned quiz
        data = {
            "quiz_id": other_quiz.id,
            "accepted": True,
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request returned a 404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User is not assigned to the quiz.")


class SetQuizStatusTests(TestCase):
    def setUp(self):
        # Create a user with the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can manage quizzes", level=1)
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        UserProfile.objects.create(user=self.user, role=self.creator_role)

        self.client = APIClient()

        # Create quiz statuses and a quiz
        self.draft_status = QuizStatus.objects.create(name="Draft", description="Quiz is in draft state")
        self.published_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz",
            description="This is a sample quiz",
            created_by=self.user,
            status=self.draft_status,
        )

        # The URL for the set_quiz_status endpoint
        self.url = reverse("set_quiz_status")

    def test_set_quiz_status_to_published(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Add a question with an answer to the quiz
        question = Question.objects.create(quiz=self.quiz, question="What is the capital of France?")
        question.answers.create(answer="Paris", is_correct=True)

        # Data to set the quiz status to Published
        data = {
            "quiz_id": self.quiz.id,
            "status": "Published",
        }

        # Update the quiz status
        response = self.client.post(self.url, data, format="json")

        # Check that the status was updated successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.status.name, "Published")

    def test_set_quiz_status_with_nonexistent_quiz(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Data with a non-existent quiz ID
        data = {
            "quiz_id": 999,  # This quiz does not exist
            "status": "Published",
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the request returned a 404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Quiz does not exist.")


class GetUserQuizzesTests(TestCase):
    def setUp(self):
        # Create a user with the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can manage quizzes", level=1)
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        UserProfile.objects.create(user=self.user, role=self.creator_role)

        self.client = APIClient()

        # Create a quiz status and some quizzes
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        Quiz.objects.create(title="Quiz 1", description="First quiz", created_by=self.user, status=self.quiz_status)
        Quiz.objects.create(title="Quiz 2", description="Second quiz", created_by=self.user, status=self.quiz_status)

        # The URL for the get_user_quizzes endpoint
        self.url = reverse("get_user_quizzes")

    def test_get_user_quizzes(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Get the user's quizzes
        response = self.client.get(self.url)

        # Check that the quizzes were retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class GetAssignedQuizzesTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")

        self.client = APIClient()

        # Create a quiz status and a quiz
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        quiz = Quiz.objects.create(
            title="Sample Quiz", description="This is a sample quiz", created_by=self.user, status=self.quiz_status
        )

        # Assign the quiz to the user
        AssignedQuiz.objects.create(user=self.user, quiz=quiz)

        # The URL for the get_assigned_quizzes endpoint
        self.url = reverse("get_assigned_quizzes")

    def test_get_assigned_quizzes(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Get the assigned quizzes
        response = self.client.get(self.url)

        # Check that the assigned quizzes were retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class GetQuizStatusesTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user with the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can manage quizzes", level=1)
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        UserProfile.objects.create(user=self.user, role=self.creator_role)

        # Create some quiz statuses
        QuizStatus.objects.create(name="Draft", description="Quiz is in draft state")
        QuizStatus.objects.create(name="Published", description="Quiz is published")
        QuizStatus.objects.create(name="Archived", description="Quiz is archived")

        # The URL for the get_quiz_statuses endpoint
        self.url = reverse("get_quiz_statuses")

    def test_get_quiz_statuses(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Get the quiz statuses
        response = self.client.get(self.url)

        print(response.data)

        # Check that the statuses were retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


class GetAvailableUserRolesTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user with the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can manage roles", level=1)
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        UserProfile.objects.create(user=self.user, role=self.creator_role)

        # Create some roles
        Role.objects.create(name="Admin", description="Administrator role", level=1)
        Role.objects.create(name="Creator", description="Content creator role", level=2)
        Role.objects.create(name="User", description="Regular user role", level=3)

        # The URL for the get_available_user_roles endpoint
        self.url = reverse("get_available_user_roles")

    def test_get_available_user_roles(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Get the available user roles
        response = self.client.get(self.url)

        # Check that the roles were retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)


class GetQuestionsByQuizTests(TestCase):
    def setUp(self):
        # Create a user with the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can manage quizzes", level=1)
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        UserProfile.objects.create(user=self.user, role=self.creator_role)

        self.client = APIClient()

        # Create a quiz and some questions
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz", description="This is a sample quiz", created_by=self.user, status=self.quiz_status
        )
        question = Question.objects.create(quiz=self.quiz, question="What is the capital of France?")

        Answer.objects.create(question=question, answer="Paris", is_correct=True)
        # The URL for the get_questions_by_quiz endpoint
        self.url = reverse("get_questions_by_quiz")

    def test_get_questions_by_quiz(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Make the request with the quiz ID as a query parameter
        response = self.client.get(self.url, {"quiz_id": self.quiz.id})

        # Check that the questions were retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class GetParticipantQuizProgressTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")

        self.client = APIClient()

        # Create a quiz status and a quiz
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz", description="This is a sample quiz", created_by=self.user, status=self.quiz_status
        )

        # Create questions and answers
        self.question1 = Question.objects.create(quiz=self.quiz, question="What is the capital of France?")
        self.answer1 = Answer.objects.create(question=self.question1, answer="Paris", is_correct=True)
        self.answer2 = Answer.objects.create(question=self.question1, answer="Lyon", is_correct=False)

        self.question2 = Question.objects.create(quiz=self.quiz, question="What is 2 + 2?")
        self.answer3 = Answer.objects.create(question=self.question2, answer="4", is_correct=True)
        self.answer4 = Answer.objects.create(question=self.question2, answer="3", is_correct=False)

        # Create user quiz progress and answered questions
        self.user_progress = UserQuizProgress.objects.create(user=self.user, quiz=self.quiz)
        AnsweredQuestion.objects.create(progress=self.user_progress, question=self.question1, answer=self.answer1)

        # The URL for the get_participant_quiz_progress endpoint
        self.url = reverse("get_participant_quiz_progress")

    def test_get_participant_quiz_progress(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Make the request with the quiz ID as a query parameter
        response = self.client.get(self.url, {"quiz_id": self.quiz.id})

        # Check that the progress was retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz"], "Sample Quiz")
        self.assertEqual(response.data["questions_answered"], 1)
        self.assertEqual(response.data["total_questions"], 2)
        self.assertEqual(response.data["correct_answers"], 3)
        self.assertEqual(response.data["total_answers"], 4)


class GetQuizScoresTests(TestCase):
    def setUp(self):
        # Create a user with the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can manage quizzes", level=1)
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        UserProfile.objects.create(user=self.user, role=self.creator_role)

        self.client = APIClient()

        # Create a quiz status and a quiz
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz", description="This is a sample quiz", created_by=self.user, status=self.quiz_status
        )

        # Create another user and their quiz progress
        self.participant = User.objects.create_user(
            username="participant", password="password123", email="participant@example.com"
        )
        self.user_progress = UserQuizProgress.objects.create(user=self.participant, quiz=self.quiz)

        # Create questions and answers
        self.question1 = Question.objects.create(quiz=self.quiz, question="What is the capital of France?")
        self.answer1 = Answer.objects.create(question=self.question1, answer="Paris", is_correct=True)

        self.question2 = Question.objects.create(quiz=self.quiz, question="What is 2 + 2?")
        self.answer2 = Answer.objects.create(question=self.question2, answer="4", is_correct=True)

        # Create answered questions
        AnsweredQuestion.objects.create(progress=self.user_progress, question=self.question1, answer=self.answer1)
        AnsweredQuestion.objects.create(progress=self.user_progress, question=self.question2, answer=self.answer2)

        # The URL for the get_quiz_scores endpoint
        self.url = reverse("get_quiz_scores")

    def test_get_quiz_scores(self):
        # Authenticate the creator user
        self.client.login(username="testuser", password="password123")

        # Make the request with the quiz ID as a query parameter
        response = self.client.get(self.url, {"quiz_id": self.quiz.id})

        # Check that the scores were retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], "participant")
        self.assertEqual(response.data[0]["correct_answers"], 2)
        self.assertEqual(response.data[0]["total_questions"], 2)

    def test_get_quiz_scores_forbidden_for_non_creator(self):
        # Authenticate as a different user who is not the creator of the quiz
        non_creator = User.objects.create_user(
            username="noncreator", password="password123", email="noncreator@example.com"
        )
        self.client.login(username="noncreator", password="password123")

        # Make the request with the quiz ID as a query parameter
        response = self.client.get(self.url, {"quiz_id": self.quiz.id})

        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetNextQuestionTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")

        self.client = APIClient()

        # Create a quiz status and a quiz
        self.quiz_status = QuizStatus.objects.create(name="Published", description="Quiz is published")
        self.quiz = Quiz.objects.create(
            title="Sample Quiz", description="This is a sample quiz", created_by=self.user, status=self.quiz_status
        )

        # Create questions for the quiz
        self.question1 = Question.objects.create(quiz=self.quiz, question="What is the capital of France?")
        self.question2 = Question.objects.create(quiz=self.quiz, question="What is 2 + 2?")

        # Create user quiz progress
        self.user_progress = UserQuizProgress.objects.create(
            user=self.user, quiz=self.quiz, last_answered_question=self.question1
        )

        # create answers for the questions
        self.answer1 = Answer.objects.create(question=self.question1, answer="Paris", is_correct=True)
        self.answer2 = Answer.objects.create(question=self.question2, answer="4", is_correct=True)

        # The URL for the get_next_question endpoint
        self.url = reverse("get_next_question")

    def test_get_next_question(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Make the request with the quiz ID as a query parameter
        response = self.client.get(self.url, {"quiz_id": self.quiz.id})

        # Check that the next question was retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question"], "What is 2 + 2?")

    def test_get_next_question_quiz_completed(self):
        # Authenticate the user
        self.client.login(username="testuser", password="password123")

        # Mark all questions as answered
        AnsweredQuestion.objects.create(progress=self.user_progress, question=self.question2, answer=self.answer2)

        # Make the request with the quiz ID as a query parameter
        response = self.client.get(self.url, {"quiz_id": self.quiz.id})

        # Check that the quiz is marked as completed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Quiz completed.")


class GetAllUsersTests(TestCase):
    def setUp(self):
        # Create a user with the Creator role
        self.creator_role = Role.objects.create(name="Creator", description="Can manage users", level=1)
        self.creator_user = User.objects.create_user(
            username="creator", password="password123", email="creator@example.com"
        )
        UserProfile.objects.create(user=self.creator_user, role=self.creator_role)

        # Create some additional users
        User.objects.create_user(username="user1", password="password123", email="user1@example.com")
        User.objects.create_user(username="user2", password="password123", email="user2@example.com")

        self.client = APIClient()

        # The URL for the get_all_users endpoint
        self.url = reverse("get_all_users")

    def test_get_all_users(self):
        # Authenticate the creator user
        self.client.login(username="creator", password="password123")

        # Get the list of all users
        response = self.client.get(self.url)

        # Check that the users were retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
