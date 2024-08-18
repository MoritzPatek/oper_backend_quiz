from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.response import Response

from rest_framework import status

from .serializers import AnsweredQuestionSerializer
from .serializers import AssignedQuizSerializer
from .serializers import QuizStatusSerializer
from .serializers import QuestionSerializer
from .serializers import AnswerSerializer
from .serializers import UserSerializer
from .serializers import QuizSerializer
from .serializers import RoleSerializer

from .decorators import role_required

from .models import AnsweredQuestion
from .models import UserQuizProgress
from .models import AssignedQuiz
from .models import QuizStatus
from .models import Question
from .models import Quiz
from .models import User
from .models import Role
from .models import Answer


@swagger_auto_schema(method="post", request_body=UserSerializer)
@api_view(["POST"])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="post", request_body=QuizSerializer)
@api_view(["POST"])
@role_required("Creator")
def create_quiz(request):
    serializer = QuizSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="post", request_body=QuestionSerializer)
@api_view(["POST"])
@role_required("Creator")
def create_question(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="post", request_body=AnswerSerializer)
@api_view(["POST"])
@role_required("Creator")
def create_answer(request):
    # check if the quiz was made by the request user
    question_id = request.data.get("question_id")
    question = Question.objects.get(id=question_id)
    quiz = question.quiz
    if quiz.created_by != request.user:
        return Response(
            {"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN
        )
    serializer = AnswerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "question_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the question"),
            "answer_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the answer"),
        },
    ),
    responses={200: AnsweredQuestionSerializer},
)
@api_view(["POST"])
def create_answered_question(request):
    user = request.user
    question_id = request.data.get("question_id")
    answer_id = request.data.get("answer_id")

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({"error": "Question does not exist."}, status=status.HTTP_404_NOT_FOUND)

    try:
        answer = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return Response({"error": "Answer does not exist."}, status=status.HTTP_404_NOT_FOUND)

    quiz = question.quiz
    user_progress = UserQuizProgress.objects.get(user=user, quiz=quiz)

    if not user_progress:
        return Response({"error": "User does not have access to the question."}, status=status.HTTP_403_FORBIDDEN)

    # Check if the answer for this question has already been answered
    answered_question = AnsweredQuestion.objects.filter(progress=user_progress, question=question, answer=answer)
    if answered_question.exists():
        # since multiple answers can be correct for one question, we don't want to raise an error but just return the
        # answer that was already answered
        user_progress.last_answered_question = question
        user_progress.save()
        serializer = AnsweredQuestionSerializer(answered_question.first())
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        # Crate a new answered question
        new_answered_question = AnsweredQuestion.objects.create(
            progress=user_progress, question=question, answer=answer
        )
        user_progress.last_answered_question = question
        user_progress.save()
        serializer = AnsweredQuestionSerializer(new_answered_question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "quiz_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the quiz"),
            "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the user"),
        },
    ),
)
@api_view(["POST"])
@role_required("Creator")
def set_quiz_to_user(request):
    quiz_id = request.data.get("quiz_id")
    user_id = request.data.get("user_id")

    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz does not exist."}, status=status.HTTP_404_NOT_FOUND)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    if quiz.status.name == "Draft":
        return Response({"error": "Quiz is still in draft status."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        AssignedQuiz.objects.get(user=user, quiz=quiz)
        return Response({"error": "User already assigned to the quiz."}, status=status.HTTP_400_BAD_REQUEST)
    except AssignedQuiz.DoesNotExist:
        pass

    serializer = AssignedQuizSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "quiz_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the quiz"),
            "accepted": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Accepted status"),
        },
    ),
)
@api_view(["POST"])
def set_accepted_status(request):
    quiz_id = request.data.get("quiz_id")
    accepted = request.data.get("accepted")

    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz does not exist."}, status=status.HTTP_404_NOT_FOUND)

    try:
        assigned_quiz = AssignedQuiz.objects.get(user=request.user, quiz=quiz)
    except AssignedQuiz.DoesNotExist:
        return Response({"error": "User is not assigned to the quiz."}, status=status.HTTP_404_NOT_FOUND)

    if accepted:
        try:
            UserQuizProgress.objects.create(user=request.user, quiz=quiz)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            UserQuizProgress.objects.get(user=request.user, quiz=quiz).delete()
        except UserQuizProgress.DoesNotExist:
            return Response({"error": "User has not started the quiz."}, status=status.HTTP_400_BAD_REQUEST)

    assigned_quiz.accepted = accepted
    assigned_quiz.save()

    return Response({"message": "Accepted status updated successfully."}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "quiz_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the quiz"),
            "status": openapi.Schema(type=openapi.TYPE_STRING, description="New status of the quiz"),
        },
    ),
)
@api_view(["POST"])
@role_required("Creator")
def set_quiz_status(request):
    quiz_id = request.data.get("quiz_id")
    quiz_status = request.data.get("status")

    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz does not exist."}, status=status.HTTP_404_NOT_FOUND)

    try:
        quiz_status = QuizStatus.objects.get(name=quiz_status)
    except QuizStatus.DoesNotExist:
        return Response({"error": "Status does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    if quiz_status.name == "Published":
        # Check if this quiz has questions that have no answers
        questions = Question.objects.filter(quiz=quiz)
        for question in questions:
            if not Answer.objects.filter(question=question).exists():
                question_ids = [q.id for q in questions if not Answer.objects.filter(question=q).exists()]
                return Response(
                    {
                        "error": f"The Questions with IDs {question_ids} do not have answers. "
                        "Please add answers to all questions before publishing the quiz."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

    quiz.status = quiz_status
    quiz.save()

    return Response({"message": "Quiz status updated successfully."}, status=status.HTTP_200_OK)


@swagger_auto_schema(method="get", responses={200: QuizSerializer(many=True)})
@api_view(["GET"])
@role_required("Creator")
def get_user_quizzes(request):
    user = request.user
    quizzes = Quiz.objects.filter(created_by=user)
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method="get", responses={200: AssignedQuizSerializer(many=True)})
@api_view(["GET"])
def get_assigned_quizzes(request):
    user = request.user
    assigned_quizzes = AssignedQuiz.objects.filter(user=user)
    serializer = AssignedQuizSerializer(assigned_quizzes, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method="get", responses={200: QuizStatusSerializer(many=True)})
@api_view(["GET"])
def get_quiz_statuses(request):
    statuses = QuizStatus.objects.all()
    serializer = QuizStatusSerializer(statuses, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method="get", responses={200: RoleSerializer(many=True)})
@api_view(["GET"])
def get_available_user_roles(request):
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("quiz_id", openapi.IN_QUERY, description="ID of the quiz", type=openapi.TYPE_INTEGER)
    ],
    responses={200: QuestionSerializer(many=True)},
)
@api_view(["GET"])
@role_required("Creator")
def get_questions_by_quiz(request):
    quiz_id = request.data.get("quiz_id")
    questions = Question.objects.filter(quiz=quiz_id)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("quiz_id", openapi.IN_QUERY, description="ID of the quiz", type=openapi.TYPE_INTEGER)
    ],
)
@api_view(["GET"])
def get_participant_quiz_progress(request):
    user = request.user
    quiz_id = request.data.get("quiz_id")
    quiz = Quiz.objects.get(id=quiz_id)
    user_progress = UserQuizProgress.objects.get(user=user, quiz=quiz)
    answered_questions = AnsweredQuestion.objects.filter(progress=user_progress)
    total_questions = Question.objects.filter(quiz=quiz)

    questions_answered_count = 0
    questions_answered = []

    correct_answers = 0
    total_answers = 0

    for question in total_questions:
        answers = Answer.objects.filter(question=question)
        for answer in answers:
            total_answers += 1

            if AnsweredQuestion.objects.filter(progress=user_progress, question=question, answer=answer).exists():
                if answer.is_correct:
                    correct_answers += 1
            else:
                if not answer.is_correct:
                    correct_answers += 1

    # answered questions sometimes answer the same question multiple times, so we need to get the unique questions
    for answered_question in answered_questions:
        if answered_question.question not in questions_answered:
            questions_answered.append(answered_question.question)
            questions_answered_count += 1

    progress = {
        "quiz": quiz.title,
        "completed": True if questions_answered_count == total_questions.count() else False,
        "questions_answered": questions_answered_count,
        "total_questions": total_questions.count(),
        "correct_answers": correct_answers,
        "total_answers": total_answers,
    }
    return Response(progress)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("quiz_id", openapi.IN_QUERY, description="ID of the quiz", type=openapi.TYPE_INTEGER)
    ],
)
@api_view(["GET"])
@role_required("Creator")
def get_quiz_scores(request):
    user = request.user
    quiz_id = request.data.get("quiz_id")
    quiz = Quiz.objects.get(id=quiz_id)

    scores = []

    if quiz.created_by != user:
        return Response({"error": "You do not have permission to view this quiz."}, status=status.HTTP_403_FORBIDDEN)

    user_progresses = UserQuizProgress.objects.filter(quiz=quiz)
    for user_progress in user_progresses:
        answered_questions = AnsweredQuestion.objects.filter(progress=user_progress)
        total_questions = Question.objects.filter(quiz=quiz)

        questions_answered_count = 0
        questions_answered = []

        correct_answers = 0
        total_answers = 0

        for question in total_questions:
            answers = Answer.objects.filter(question=question)
            for answer in answers:
                total_answers += 1

                if AnsweredQuestion.objects.filter(progress=user_progress, question=question, answer=answer).exists():
                    if answer.is_correct:
                        correct_answers += 1
                else:
                    if not answer.is_correct:
                        correct_answers += 1

        # answered questions sometimes answer the same question multiple times, so we need to get the unique questions
        for answered_question in answered_questions:
            if answered_question.question not in questions_answered:
                questions_answered.append(answered_question.question)
                questions_answered_count += 1

        progress = {
            "user": user_progress.user.username,
            "completed": True if questions_answered_count == total_questions.count() else False,
            "questions_answered": questions_answered_count,
            "total_questions": total_questions.count(),
            "correct_answers": correct_answers,
            "total_answers": total_answers,
        }
        scores.append(progress)

    return Response(scores)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("quiz_id", openapi.IN_QUERY, description="ID of the quiz", type=openapi.TYPE_INTEGER)
    ],
    responses={200: QuestionSerializer},
)
@api_view(["GET"])
def get_next_question(request):
    user = request.user
    quiz_id = request.data.get("quiz_id")
    quiz = Quiz.objects.get(id=quiz_id)
    user_progress = UserQuizProgress.objects.get(user=user, quiz=quiz)
    last_answered_question = user_progress.last_answered_question
    questions = Question.objects.filter(quiz=quiz).order_by("created_at")

    if last_answered_question:
        answered_questions = AnsweredQuestion.objects.filter(progress=user_progress)
        next_question = questions.filter(created_at__gt=last_answered_question.created_at).first()
        if AnsweredQuestion.objects.filter(progress=user_progress, question=next_question).exists():
            next_question = (
                questions.filter(created_at__gt=last_answered_question.created_at)
                .exclude(id__in=[a.question.id for a in answered_questions])
                .first()
            )
        if not next_question:
            user_progress.completed = True
            return Response({"message": "Quiz completed."}, status=status.HTTP_200_OK)
    else:
        next_question = questions.first()

    serializer = QuestionSerializer(next_question)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("question_id", openapi.IN_QUERY, description="ID of the question", type=openapi.TYPE_INTEGER)
    ],
    responses={200: AnswerSerializer(many=True)},
)
@api_view(["GET"])
def get_answers_by_question(request):
    question_id = request.data.get("question_id")
    user = request.user
    quiz = Question.objects.get(id=question_id).quiz

    # Check if quiz is Published
    if quiz.status.name != "Published":
        return Response({"error": "Quiz is not published."}, status=status.HTTP_400_BAD_REQUEST)

    user_progress = UserQuizProgress.objects.get(user=user, quiz=quiz)

    if not user_progress:
        return Response({"error": "User does not have access to the question."}, status=status.HTTP_403_FORBIDDEN)

    answers = Answer.objects.filter(question=question_id)
    serializer = AnswerSerializer(answers, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method="get", responses={200: UserSerializer(many=True)})
@api_view(["GET"])
@role_required("Creator")
def get_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
