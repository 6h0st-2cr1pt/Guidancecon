from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        
        # Try to find user by email first
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            pass
        except MultipleObjectsReturned:
            # If multiple users have the same email, get the first one (prefer staff users)
            user = User.objects.filter(email=username).order_by('-is_staff', '-is_superuser', 'id').first()
        
        # If not found by email, try username
        if user is None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
            except MultipleObjectsReturned:
                # If multiple users have the same username (shouldn't happen, but handle it)
                user = User.objects.filter(username=username).order_by('-is_staff', '-is_superuser', 'id').first()
        
        # Check password
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
