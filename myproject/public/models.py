from django.db import models
from django.conf import settings


# Profile for public users (students)
class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
	student_id = models.CharField(max_length=50, unique=True)
	course = models.CharField(max_length=255, blank=True)
	year_level = models.CharField(max_length=50, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Profile for {self.user.username}"
