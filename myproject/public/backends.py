from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile

class StudentIDBackend(ModelBackend):
    """
    Custom authentication backend that allows students to login with their student ID.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # First try to find user by student ID
            profile = UserProfile.objects.get(student_id=username)
            user = profile.user
        except UserProfile.DoesNotExist:
            try:
                # Fallback to email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                try:
                    # Final fallback to username
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return None
        
        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None