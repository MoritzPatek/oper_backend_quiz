from rest_framework import serializers
from django.contrib.auth.models import User

from .models import AnsweredQuestion
from .models import UserQuizProgress
from .models import AssignedQuiz
from .models import UserProfile
from .models import QuizStatus
from .models import Question
from .models import Answer
from .models import Role
from .models import Quiz


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True)
    role_name = serializers.CharField(source="userprofile.role.name", read_only=True)

    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role", "role_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Extract role name and remove it from validated data
        role_name = validated_data.pop("role")

        # Create the user
        try:
            user = User.objects.create_user(**validated_data)
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

        # Find the role object
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            user.delete()
            raise serializers.ValidationError({"error": "Role does not exist."})

        # Create the UserProfile with the role
        try:
            UserProfile.objects.create(user=user, role=role)
        except Exception as e:
            user.delete()
            raise serializers.ValidationError({"error": str(e)})

        return user


class RoleSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Role
        fields = ["id", "name", "description", "level"]

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class QuizStatusSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = QuizStatus
        fields = ["id", "name", "description"]

    def create(self, validated_data):
        return super().create(validated_data)


class QuizSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "description"]

    def create(self, validated_data):
        status = QuizStatus.objects.get(name="Draft")
        # Automatically set the creator of the quiz
        validated_data["created_by"] = self.context["request"].user
        validated_data["status"] = status

        return super().create(validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    quiz_id = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), source="quiz", write_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Question
        fields = ["id", "question", "quiz_id"]

    def create(self, validated_data):
        # check if the quiz is in Draft status
        if validated_data["quiz"].status.name != "Draft":
            raise serializers.ValidationError({"error": "Questions can only be added to quizzes in Draft status."})

        # The quiz is automatically set by the PrimaryKeyRelatedField
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), source="question", write_only=True
    )
    id = serializers.ReadOnlyField()

    class Meta:
        model = Answer
        fields = ["id", "answer", "is_correct", "question_id"]

    def create(self, validated_data):
        # check if the question is in Draft status
        if validated_data["question"].quiz.status.name != "Draft":
            raise serializers.ValidationError({"error": "Answers can only be added to questions in Draft status."})

        # The question is automatically set by the PrimaryKeyRelatedField
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["question_id"] = instance.question.id
        return representation


class AssignedQuizSerializer(serializers.ModelSerializer):
    quiz_id = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), source="quiz", write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user", write_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = AssignedQuiz
        fields = ["id", "quiz_id", "user_id", "accepted"]

    def create(self, validated_data):
        # set accepted as False by default
        validated_data["accepted"] = False
        # The creation logic is handled automatically by the serializer
        return super().create(validated_data)

    # make sure quiz_id and user_id are getting displayed
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["quiz_id"] = instance.quiz.id
        representation["user_id"] = instance.user.id
        return representation


class UserQuizProgressSerializer(serializers.ModelSerializer):
    quiz_id = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), source="quiz", write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user", write_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = UserQuizProgress
        fields = ["id", "quiz_id", "user_id", "score", "completed"]

    def create(self, validated_data):
        # set accepted as False by default
        validated_data["completed"] = False
        # The creation logic is handled automatically by the serializer
        return super().create(validated_data)

    # make sure quiz_id and user_id are getting displayed
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["quiz_id"] = instance.quiz.id
        representation["user_id"] = instance.user.id
        return representation


class AnsweredQuestionSerializer(serializers.ModelSerializer):
    user_progress_id = serializers.PrimaryKeyRelatedField(
        queryset=UserQuizProgress.objects.all(), source="user_progress", write_only=True
    )
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), source="question", write_only=True
    )
    answer_id = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all(), source="answer", write_only=True)
    id = serializers.ReadOnlyField()

    is_correct = serializers.BooleanField(read_only=True)

    class Meta:
        model = AnsweredQuestion
        fields = ["id", "user_progress_id", "question_id", "answer_id", "is_correct"]

    def create(self, validated_data):
        # The creation logic is handled automatically by the serializer
        return super().create(validated_data)

    # make sure user_progress_id and question_id are getting displayed
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user_progress_id"] = instance.progress.id
        representation["question_id"] = instance.question.id
        representation["answer_id"] = instance.answer.id
        representation["is_correct"] = instance.answer.is_correct
        return representation
