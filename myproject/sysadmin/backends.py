from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email first
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                # Fallback to username
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        # Only allow login if user is staff (counselor/admin)
        if user.check_password(password) and self.user_can_authenticate(user) and user.is_staff:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
