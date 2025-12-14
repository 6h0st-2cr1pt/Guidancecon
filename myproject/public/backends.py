from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from .models import UserProfile

class StudentIDBackend(ModelBackend):
    """
    Custom authentication backend that allows students to login with their student ID.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        
        # First try to find user by student ID
        try:
            profile = UserProfile.objects.get(student_id=username)
            user = profile.user
        except UserProfile.DoesNotExist:
            pass
        except MultipleObjectsReturned:
            # If multiple profiles have the same student_id, get the first one
            profile = UserProfile.objects.filter(student_id=username).first()
            if profile:
                user = profile.user
        
        # If not found by student ID, try email
        if user is None:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                pass
            except MultipleObjectsReturned:
                # If multiple users have the same email, prefer non-staff users (students)
                user = User.objects.filter(email=username).order_by('is_staff', 'id').first()
        
        # If still not found, try username
        if user is None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
            except MultipleObjectsReturned:
                # If multiple users have the same username (shouldn't happen, but handle it)
                user = User.objects.filter(username=username).order_by('is_staff', 'id').first()
        
        # Check password
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None