from functools import wraps
from django.http import JsonResponse
from .models import UserProfile


def role_required(required_role):
    """
    Decorator to check if the user has the required role.
    :param required_role: The role required to access the view.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication credentials were not provided."}, status=401)

            # Get the user's role
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                user_role = user_profile.role.name if user_profile.role else None

                # Check if the user has the required role
                if user_role != required_role:
                    return JsonResponse({"error": "You do not have permission to perform this action."}, status=403)
            except UserProfile.DoesNotExist:
                return JsonResponse({"error": "User profile does not exist."}, status=403)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
