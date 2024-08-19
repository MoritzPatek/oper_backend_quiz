"""
This file is used to register the models in the admin panel.
"""

from django.contrib import admin

from .models import UserQuizProgress
from .models import AnsweredQuestion
from .models import AssignedQuiz
from .models import UserProfile
from .models import QuizStatus
from .models import Question
from .models import Answer
from .models import Role
from .models import Quiz

admin.site.register(UserQuizProgress)
admin.site.register(AnsweredQuestion)
admin.site.register(AssignedQuiz)
admin.site.register(UserProfile)
admin.site.register(QuizStatus)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Role)
admin.site.register(Quiz)
