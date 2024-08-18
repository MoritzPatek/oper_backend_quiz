from django.urls import path

from .views import get_participant_quiz_progress
from .views import get_available_user_roles
from .views import get_answers_by_question
from .views import get_questions_by_quiz
from .views import get_assigned_quizzes
from .views import get_next_question
from .views import get_quiz_statuses
from .views import get_user_quizzes
from .views import get_quiz_scores
from .views import get_all_users

from .views import create_answered_question
from .views import create_question
from .views import create_answer
from .views import create_quiz
from .views import create_user

from .views import set_accepted_status
from .views import set_quiz_to_user
from .views import set_quiz_status


urlpatterns = [
    path("get_participant_quiz_progress/", get_participant_quiz_progress, name="get_participant_quiz_progress"),
    path("get_available_user_roles/", get_available_user_roles, name="get_available_user_roles"),
    path("get_answers_by_question/", get_answers_by_question, name="get_answers_by_question"),
    path("get_questions_by_quiz/", get_questions_by_quiz, name="get_questions_by_quiz"),
    path("get_assigned_quizzes/", get_assigned_quizzes, name="get_assigned_quizzes"),
    path("get_next_question/", get_next_question, name="get_next_question"),
    path("get_quiz_statuses/", get_quiz_statuses, name="get_quiz_statuses"),
    path("get_user_quizzes/", get_user_quizzes, name="get_user_quizzes"),
    path("get_quiz_scores/", get_quiz_scores, name="get_quiz_scores"),
    path("get_all_users/", get_all_users, name="get_all_users"),
    ############################
    path("create_answered_question/", create_answered_question, name="create_answered_question"),
    path("create_question/", create_question, name="create_question"),
    path("create_answer/", create_answer, name="create_answer"),
    path("create_quiz/", create_quiz, name="create_quiz"),
    path("create_user/", create_user, name="create_user"),
    ############################
    path("set_accepted_status/", set_accepted_status, name="set_accepted_status"),
    path("set_quiz_to_user/", set_quiz_to_user, name="set_quiz_to_user"),
    path("set_quiz_status/", set_quiz_status, name="set_quiz_status"),
]
