from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from ...models import Role, QuizStatus, UserProfile
import os


class Command(BaseCommand):
    help = "Initialize the database with user roles and quiz states, and create initial users."

    def handle(self, *args, **kwargs):
        self.init_roles()
        self.init_quiz_states()
        self.create_initial_users()

    def init_roles(self):
        roles = [
            {"name": "Creator", "description": "User who creates quizzes", "level": 1},
            {"name": "Participant", "description": "User who takes quizzes", "level": 2},
        ]

        for role_data in roles:
            role, created = Role.objects.get_or_create(name=role_data["name"], defaults=role_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created role: {role.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Role already exists: {role.name}"))

    def init_quiz_states(self):
        states = [
            {"name": "Draft", "description": "Quiz is still being created"},
            {"name": "Published", "description": "Quiz is published and available for participants"},
            {"name": "Closed", "description": "Quiz is closed and no longer available"},
        ]

        for state_data in states:
            state, created = QuizStatus.objects.get_or_create(name=state_data["name"], defaults=state_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created quiz state: {state.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Quiz state already exists: {state.name}"))

    @transaction.atomic
    def create_initial_users(self):
        # Get environment variables
        creator_username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        creator_password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        creator_email = os.getenv("DJANGO_SUPERUSER_EMAIL")

        if not creator_username or not creator_password or not creator_email:
            self.stdout.write(self.style.ERROR("Environment variables for the superuser are not set properly."))
            return

        # Creating the Creator user
        creator_role = Role.objects.get(name="Creator")

        creator_user, created = User.objects.get_or_create(
            username=creator_username, defaults={"email": creator_email, "is_superuser": True, "is_staff": True}
        )
        if created:
            creator_user.set_password(creator_password)
            creator_user.save()
            UserProfile.objects.create(user=creator_user, role=creator_role)
            self.stdout.write(self.style.SUCCESS(f"Created user: {creator_user.username} with role Creator"))
        else:
            self.stdout.write(self.style.WARNING(f"User already exists: {creator_user.username}"))
            # Ensure the profile exists and is updated with the correct role
            profile, _ = UserProfile.objects.get_or_create(user=creator_user, defaults={"role": creator_role})
            profile.role = creator_role
            profile.save()

        # Creating the Participant user
        participant_role = Role.objects.get(name="Participant")
        participant_user, created = User.objects.get_or_create(
            username="Oper", defaults={"email": "oper@example.com", "is_superuser": False, "is_staff": False}
        )
        if created:
            participant_user.set_password("Oper")
            participant_user.save()
            UserProfile.objects.create(user=participant_user, role=participant_role)
            self.stdout.write(self.style.SUCCESS(f"Created user: {participant_user.username} with role Participant"))
        else:
            self.stdout.write(self.style.WARNING(f"User already exists: {participant_user.username}"))
            # Ensure the profile exists and is updated with the correct role
            profile, _ = UserProfile.objects.get_or_create(user=participant_user, defaults={"role": participant_role})
            profile.role = participant_role
            profile.save()
